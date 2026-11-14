# Material de estudo: Historico do cliente

Este guia explica, passo a passo e sem pressa, a quarta funcionalidade do projeto.
Para a versao resumida (tabelas e arquivos), veja [HISTORICO-CLIENTE.md](HISTORICO-CLIENTE.md).

## 1. A ideia em uma frase

Na lista de clientes, cada cliente ganhou um botao **Historico**. Ele abre uma
pagina que mostra *tudo o que aquele cliente ja fez no sistema*: quanto gastou,
quando veio pela ultima vez, quando volta e a lista de todos os agendamentos.

Pense na "ficha do cliente" de uma barbearia, so que automatica.

## 2. Por que nao precisou mexer no banco de dados?

Todos os dados que a tela mostra **ja existiam**:

- O cliente (`Cliente`): nome, telefone, e-mail.
- Os agendamentos dele (`Agendamento`): data, situacao e o servico escolhido.
- O preco (`Servico.preco`): vem do servico de cada agendamento.

Entao a funcionalidade so **le e organiza** esses dados. Por isso nao existe
migration nova (migration = arquivo que altera as tabelas do banco).

O elo entre cliente e agendamentos ja existia no model, neste trecho:

```python
cliente = models.ForeignKey(Cliente, ..., related_name="agendamentos")
```

O `related_name="agendamentos"` e o que permite escrever `cliente.agendamentos`
e receber todos os agendamentos daquele cliente.

## 3. O caminho completo: do clique ate a tela

```
Navegador                Django                          Banco de dados
   |                        |                                  |
   | 1. clica "Historico"   |                                  |
   |----------------------->|                                  |
   |   GET /clientes/3/historico/                              |
   |                        | 2. urls.py acha a rota           |
   |                        | 3. views.cliente_historico(pk=3) |
   |                        |--------------------------------->|
   |                        |   busca o cliente 3 e os         |
   |                        |   agendamentos dele              |
   |                        |<---------------------------------|
   |                        | 4. monta o "resumo"              |
   |                        | 5. renderiza o template          |
   |<-----------------------|                                  |
   | 6. recebe a pagina HTML                                   |
```

Cada passo mora em um arquivo:

| Passo | Arquivo | O que faz |
|---|---|---|
| 1 | `templates/agenda/cliente_lista.html` | Tem o botao **Historico**, que aponta para a rota |
| 2 | `agenda/urls.py` | Liga o endereco `clientes/<id>/historico/` a view |
| 3 a 4 | `agenda/views.py` | Funcao `cliente_historico`: busca e calcula |
| 5 | `templates/agenda/cliente_historico.html` | Desenha a pagina |

## 4. A rota (`agenda/urls.py`)

```python
path("clientes/<int:pk>/historico/", views.cliente_historico, name="cliente_historico"),
```

- `<int:pk>` captura o numero do cliente na URL. Em `/clientes/3/historico/`, o `pk` vale 3.
- `name="cliente_historico"` e o apelido da rota. Nos templates usamos o apelido
  (`{% url 'cliente_historico' cliente.pk %}`) em vez de escrever o endereco na mao.
  Se o endereco mudar um dia, so a rota precisa ser alterada.

## 5. A view (`agenda/views.py`), linha por linha

```python
def cliente_historico(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
```
Busca o cliente. Se o numero nao existir (ex.: `/clientes/999/historico/`), o Django
mostra a pagina de erro **404** em vez de quebrar.

```python
    agendamentos = cliente.agendamentos.select_related("servico").order_by("-inicio")
```
- `cliente.agendamentos` = so os agendamentos **deste** cliente.
- `select_related("servico")` busca o servico junto, na mesma consulta. Sem isso, a
  tabela faria uma consulta extra ao banco para cada linha (isso e uma otimizacao).
- `order_by("-inicio")` ordena do mais novo para o mais antigo (o `-` inverte a ordem).

```python
    concluidos = agendamentos.filter(status=Agendamento.Status.CONCLUIDO)
```
Separa so os atendimentos que de fato aconteceram. A regra e a mesma do faturamento:
**so agendamento concluido vira dinheiro.** Agendado ainda nao aconteceu e cancelado
nunca vai acontecer.

Depois, o dicionario `resumo` guarda os numeros mostrados nos cartoes:

| Chave | Como e calculada | Mostra |
|---|---|---|
| `total` | `agendamentos.count()` | Quantos agendamentos existem no total |
| `concluidos` | `concluidos.count()` | Atendimentos concluidos |
| `cancelados` | `filter(status=CANCELADO).count()` | Quantos foram cancelados |
| `total_gasto` | `concluidos.aggregate(t=Sum("servico__preco"))["t"] or Decimal("0")` | Soma dos precos |
| `ultimo` | `concluidos.first()` | Concluido mais recente |
| `proximo` | agendados futuros, `.last()` | Proximo horario marcado |

Tres detalhes que costumam gerar duvida:

**a) `Sum("servico__preco")`**
O duplo underline (`__`) significa "atravessar a relacao". O agendamento nao tem
preco; quem tem e o servico dele. `servico__preco` quer dizer "o preco do servico
deste agendamento". O `Sum` soma todos e o banco faz a conta (mais rapido do que somar
em Python).

**b) `or Decimal("0")`**
Se o cliente nao tem nenhum concluido, o `Sum` devolve `None` (nada para somar). Com
`or Decimal("0")` a tela mostra `R$ 0` em vez de `R$ None`.

**c) Por que `.first()` para o ultimo e `.last()` para o proximo?**
A lista esta ordenada do **mais novo para o mais antigo**.
- *Ultimo atendimento*: o concluido mais recente e o **primeiro** da lista, entao `.first()`.
- *Proximo horario*: entre os agendados futuros, o mais **proximo de agora** e o mais
  antigo deles, ou seja, o **ultimo** da lista, entao `.last()`.

O filtro `inicio__gte=timezone.now()` garante que so entram horarios de hoje em diante
(`gte` = *greater than or equal*, maior ou igual).

Por fim:

```python
    return render(request, "agenda/cliente_historico.html",
                  {"cliente": cliente, "agendamentos": agendamentos, "resumo": resumo})
```
Entrega os tres dados ao template, que monta o HTML.

## 6. O template (`templates/agenda/cliente_historico.html`)

Ele tem duas partes:

1. **Quatro cartoes** com os numeros do `resumo` (`{{ resumo.total_gasto }}` etc.).
   Onde pode nao haver valor, ha um `{% if %}` que mostra `-`:
   ```
   {% if resumo.ultimo %}{{ resumo.ultimo.inicio|date:"d/m/Y" }}{% else %}-{% endif %}
   ```
2. **A tabela** com um `{% for ag in agendamentos %}` que cria uma linha por
   agendamento. O `{% empty %}` define o texto exibido quando a lista esta vazia
   ("Este cliente ainda nao tem agendamentos"). A situacao aparece como um *badge*
   colorido: azul (agendado), verde (concluido) e cinza (cancelado).

`|date:"d/m/Y"` e `|time:"H:i"` sao filtros que formatam a data como `14/11/2026` e a
hora como `15:30`.

## 7. Exemplo pratico

Maria tem estes agendamentos:

| Data | Servico | Preco | Situacao |
|---|---|---|---|
| 04/11 | Corte | 50 | concluido |
| 09/11 | Coloracao | 180 | concluido |
| 11/11 | Coloracao | 180 | cancelado |
| 20/11 | Corte | 50 | agendado |

A tela mostra:

- **Total gasto: R$ 230** (50 + 180; o cancelado e o agendado **nao** entram)
- **Atendimentos concluidos: 2**
- **Ultimo atendimento: 09/11**
- **Proximo horario: 20/11**

## 8. Os testes (`agenda/tests.py`, classe `HistoricoClienteTests`)

Teste automatico e um codigo que usa o sistema sozinho e confere se o resultado esta certo.

| Teste | O que garante |
|---|---|
| `test_total_gasto_soma_so_concluidos_do_cliente` | Soma so concluidos, ignora cancelados e **nao mistura** com agendamentos de outro cliente |
| `test_ultimo_atendimento_e_proximo_horario` | `ultimo` e o concluido mais recente; `proximo` e o agendado futuro mais proximo |
| `test_cliente_sem_agendamentos` | Cliente novo mostra a mensagem de vazio e total `0`, sem erro |
| `test_cliente_inexistente_da_404` | Um numero que nao existe devolve 404 |
| `test_lista_de_clientes_tem_link_para_historico` | O botao **Historico** aparece na lista |

Para rodar: `python manage.py test` (deve terminar com `OK`).

## 9. Perguntas que o professor pode fazer

**Por que nao foi criada uma tabela nova?**
Porque tudo ja estava salvo em `Cliente`, `Agendamento` e `Servico`. Duplicar o dado
em outra tabela so criaria risco de ficar desatualizado.

**Por que so os concluidos contam como gasto?**
Porque so eles representam servico realizado e pago. E a mesma regra da tela de
Relatorios, entao os numeros sempre batem.

**O que acontece se o cliente nao tem agendamentos?**
A pagina abre normalmente, com total `R$ 0`, `-` nos campos de data e a mensagem de
lista vazia.

**O que acontece se alguem digitar um cliente que nao existe na URL?**
`get_object_or_404` devolve a pagina 404, sem quebrar o sistema.

**Em qual das 3 camadas esta cada parte?**
Front-end: `cliente_historico.html`. Back-end: `views.py` e `urls.py`. Banco de
dados: nenhuma mudanca, so leitura dos models existentes.

## 10. Exercicios "mexa e veja"

1. Rode `python manage.py popular_dados`, abra **Clientes** e clique em **Historico**
   de alguem. Confira os numeros contra a tabela.
2. Em **Agendamentos**, mude um agendamento para *concluido* e recarregue o
   historico: o total gasto sobe.
3. Mude esse mesmo agendamento para *cancelado*: o total gasto cai de novo.
4. Digite `/clientes/9999/historico/` na barra de endereco e veja a pagina 404.
5. Em `views.py`, troque `.last()` por `.first()` no campo `proximo`, rode os testes e
   veja qual teste falha (depois desfaca a mudanca). Isso mostra por que a ordem da
   lista importa.
