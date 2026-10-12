# Entendendo o codigo

Guia de estudo para quem vai explicar este projeto. Leia com o sistema rodando
ao lado: use uma tela, depois abra o codigo dela. Para consultar a estrutura
completa (todos os enderecos, tabelas do banco e configuracoes), veja
[ARQUITETURA.md](ARQUITETURA.md).

Indice: [1. Mapa](#1-mapa-do-projeto) |
[2. Caminho de uma requisicao](#2-o-caminho-de-uma-requisicao) |
[3. Arquivo por arquivo](#3-arquivo-por-arquivo) |
[4. Glossario](#4-glossario-django) |
[5. O professor pode perguntar](#5-o-professor-pode-perguntar) |
[6. Mexa e veja](#6-mexa-e-veja)

---

## 1. Mapa do projeto

O projeto tem **tres camadas**, e cada uma mora em um lugar:

```
 NAVEGADOR            FRONT-END               BACK-END                 BANCO DE DADOS
 (usuario)        templates/ + static/     views.py, forms.py        models.py + migrations
                                            urls.py                  db.sqlite3

  clica em   -->   HTML da tela       -->   decide o que fazer  -->  guarda e busca dados
  "Salvar"   <--   volta renderizado  <--   valida o formulario <--
```

| Camada | Responsabilidade | Arquivos |
|---|---|---|
| Front-end | O que o usuario ve | `templates/`, `static/css/` |
| Back-end | O que acontece em cada endereco | `agenda/urls.py`, `agenda/views.py`, `agenda/forms.py` |
| Dados | O que e guardado e quais as regras | `agenda/models.py`, `agenda/migrations/` |

Tres entidades, ligadas assim:

```
Cliente 1 ----< Agendamento >---- 1 Servico
```

Um cliente pode ter varios agendamentos, e um servico pode estar em varios
agendamentos. Cada `Agendamento` aponta para um cliente e um servico.

---

## 2. O caminho de uma requisicao

Vamos seguir **"criar um agendamento"** do clique ate o banco. Esta e a parte
mais importante para entender e explicar.

### Passo 1: o usuario abre `/agendamentos/novo/`

`config/urls.py` entrega tudo que nao e `/admin/` para `agenda/urls.py`, que tem:

```python
path("agendamentos/novo/", views.agendamento_novo, name="agendamento_novo"),
```

O `name="agendamento_novo"` e o apelido do endereco. Os templates usam o
apelido (`{% url 'agendamento_novo' %}`), entao se o endereco mudar, nada quebra.

### Passo 2: a view monta o formulario vazio

```python
def agendamento_novo(request):
    form = AgendamentoForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Agendamento criado com sucesso.")
        return redirect("agendamento_lista")
    return render(request, "agenda/form.html", {...})
```

Em um `GET` (abrir a pagina), `request.POST` esta vazio, entao `request.POST or None`
vira `None` e o formulario nasce **vazio**. A view cai no `render` e mostra a tela.

### Passo 3: o template desenha o formulario

`templates/agenda/form.html` e um template **generico**: serve para cliente,
servico e agendamento. Ele percorre `{% for campo in form %}` e desenha cada campo.
O titulo e o botao "Cancelar" vem do contexto (`titulo` e `voltar`).

### Passo 4: o usuario preenche e clica em Salvar

O navegador envia um `POST` para o mesmo endereco. Agora `request.POST` tem dados,
e a view faz `form.is_valid()`. Aqui comeca a validacao, em **tres niveis**:

| Nivel | Onde | O que checa |
|---|---|---|
| 1. Campo | tipo do campo no model/form | obrigatorio, tamanho, formato de data |
| 2. Campo (nossa regra) | `AgendamentoForm.clean_inicio` | nao pode ser no passado |
| 3. Modelo inteiro | `Agendamento.clean` | **conflito de horario** |

Se qualquer nivel falhar, `is_valid()` devolve `False`, a view cai no `render` de
novo e a tela volta **com os erros** e com o que o usuario digitou preservado.

### Passo 5: a regra de conflito

Esta e a regra de negocio central, em `agenda/models.py`:

```python
def conflitos(self):
    return (
        Agendamento.objects
        .exclude(status=self.Status.CANCELADO)
        .exclude(pk=self.pk)
        .filter(inicio__lt=self.calcular_fim(), fim__gt=self.inicio)
    )
```

Leia como uma frase: *"procure agendamentos que nao estejam cancelados, que nao
sejam este mesmo, e que comecem antes de este terminar e terminem depois de este
comecar."* Isso e exatamente o que significa dois horarios se sobreporem:

```
existente:   |-------|            10:00 - 10:30
novo:            |-------|        10:15 - 10:45   -> comeca antes de 10:30 E termina depois de 10:00: CONFLITO
novo:                    |----|   10:30 - 11:00   -> nao comeca ANTES de 10:30: OK
```

Por usar `<` e `>` (e nao `<=` e `>=`), um horario que so encosta no outro e aceito.

O metodo `clean()` chama `conflitos()` e, se achar algum, levanta
`ValidationError` com a mensagem "Horario indisponivel...".

### Passo 6: salvar

Se tudo passou, `form.save()` chama `Agendamento.save()`, que antes de gravar
calcula o `fim`:

```python
def save(self, *args, **kwargs):
    self.fim = self.calcular_fim()      # inicio + duracao do servico
    super().save(*args, **kwargs)
```

O Django gera o `INSERT` no SQLite. A view guarda uma mensagem de sucesso e faz
`redirect("agendamento_lista")`.

### Passo 7: redirect e mensagem

Depois de um POST bem-sucedido a view **redireciona** em vez de renderizar. Se
renderizasse, apertar F5 reenviaria o formulario e criaria um duplicado. Esse
padrao chama-se *Post/Redirect/Get*. A mensagem verde da tela vem de
`messages.success`, desenhada em `templates/base.html`.

### Outro caminho: buscar um cliente

A busca e mais simples que o cadastro: **nao ha formulario, nem validacao, nem
redirect**. So le. Siga `/clientes/?q=maria`:

1. `agenda/urls.py` entrega o endereco a `views.cliente_lista`. O `?q=maria` nao muda
   a rota: e so um parametro, que a view le.
2. A view le o parametro e filtra:

```python
def cliente_lista(request):
    busca = request.GET.get("q", "").strip()
    clientes = Cliente.objects.all()
    if busca:
        clientes = clientes.filter(Q(nome__icontains=busca) | Q(telefone__icontains=busca))
    return render(request, "agenda/cliente_lista.html", {"clientes": clientes, "busca": busca})
```

3. `Q(...) | Q(...)` e um **OU**: o nome contem o texto ou o telefone contem. O
   `icontains` quer dizer "contem, sem diferenciar maiuscula de minuscula" (com a
   limitacao de acentos descrita em [CADASTROS.md](CADASTROS.md)).
4. `clientes` ainda nao foi ao banco: a consulta so roda quando o template percorre
   `{% for cliente in clientes %}`.
5. O template devolve o campo preenchido (`value="{{ busca }}"`) e, se nada
   casar, mostra a linha do `{% empty %}`.

| | Buscar | Cadastrar |
|---|---|---|
| Metodo HTTP | `GET` | `POST` |
| Mexe no banco? | so le | grava |
| Validacao | nao tem | tres niveis |
| Termina em | pagina desenhada | `redirect` |
| Pode virar link ou favorito | sim (`/clientes/?q=maria`) | nao |

---

## 3. Arquivo por arquivo

### `config/` — configuracao do projeto
| Arquivo | Para que serve |
|---|---|
| `settings.py` | Apps instalados, banco (SQLite), idioma (`pt-br`), fuso (`America/Sao_Paulo`), pasta de templates |
| `urls.py` | Porta de entrada dos enderecos: `/admin/` vai para o admin, o resto vai para o app `agenda` |
| `wsgi.py`, `asgi.py` | Pontos de entrada para servidores de producao (nao mexemos neles) |

### `agenda/` — o app com a regra de negocio
| Arquivo | Para que serve |
|---|---|
| `models.py` | Define as tabelas (`Cliente`, `Servico`, `Agendamento`) e a regra de conflito |
| `migrations/` | Historico das mudancas no banco. `0001` cria Cliente e Servico; `0002` cria Agendamento; `0003` define a duracao minima |
| `forms.py` | Transforma models em formularios e valida. Tem o `BootstrapFormMixin` que aplica o estilo |
| `views.py` | Uma funcao por tela/acao (listar, novo, editar, excluir) |
| `urls.py` | Liga cada endereco a uma view |
| `admin.py` | Configura o painel `/admin/` (colunas, filtros, busca) |
| `tests.py` | Testes automatizados (35 no total) |
| `management/commands/popular_dados.py` | Comando que cria dados de exemplo |

### `templates/` — o HTML
| Arquivo | Para que serve |
|---|---|
| `base.html` | Esqueleto de toda pagina: menu, mensagens, Bootstrap. As outras "herdam" dele |
| `agenda/home.html` | Painel inicial com contadores e proximos horarios |
| `agenda/*_lista.html` | Tabelas de clientes, servicos e agendamentos, com busca/filtro |
| `agenda/form.html` | Formulario generico (serve para todas as entidades) |
| `agenda/confirmar_exclusao.html` | Tela "tem certeza?" antes de apagar |
| `admin/base_site.html` | Personaliza o visual do admin |

### Como o Django resolve um template
`{% extends "base.html" %}` diz "use o esqueleto de `base.html`", e
`{% block conteudo %}...{% endblock %}` preenche o espaco que o esqueleto deixou.
Assim o menu e escrito uma vez so.

---

## 4. Glossario Django

| Termo | Em portugues claro | Onde aparece aqui |
|---|---|---|
| **Model** | Uma classe Python que vira uma tabela do banco | `Cliente`, `Servico`, `Agendamento` |
| **Migration** | Receita que cria/altera tabelas. Gerada com `makemigrations`, aplicada com `migrate` | `agenda/migrations/` |
| **ORM** | Escrever consultas em Python em vez de SQL (`Cliente.objects.filter(...)`) | `views.py`, `models.py` |
| **View** | Funcao que recebe a requisicao e devolve uma resposta | `agenda/views.py` |
| **Template** | HTML com "buracos" preenchidos pelo Django (`{{ cliente.nome }}`) | `templates/` |
| **ModelForm** | Formulario gerado a partir de um model | `forms.py` |
| **`clean()`** | Gancho onde o model valida a si mesmo | `Agendamento.clean` |
| **`ValidationError`** | Excecao que significa "dado invalido" e vira mensagem na tela | `models.py`, `forms.py` |
| **`on_delete=PROTECT`** | "Nao deixe apagar este registro se algo depende dele" | FKs de `Agendamento` |
| **`get_object_or_404`** | Busca um registro ou devolve a pagina "nao encontrado" | `views.py` |
| **CSRF** | Protecao contra formularios forjados por outros sites. Por isso todo form tem `{% csrf_token %}` | todos os forms |
| **`messages`** | Avisos de uma vez so ("salvo com sucesso") entre uma pagina e outra | `views.py`, `base.html` |
| **`select_related`** | Traz cliente e servico junto na mesma consulta, evitando uma consulta por linha | `views.py` |
| **`TextChoices`** | Lista fixa de opcoes de um campo (o status) | `Agendamento.Status` |

---

## 5. O professor pode perguntar

Treine responder cada uma **em voz alta**, com suas palavras.

**Por que a regra de conflito esta no model e nao na view?**
Porque o model e o ponto onde todo salvamento passa. Se a regra ficasse na view,
o `/admin/` (que nao usa nossas views) poderia criar horarios conflitantes.
No model a regra vale em qualquer lugar. Os testes da regra chamam o
`full_clean()` direto no model, sem passar por tela nenhuma.

**Por que guardar o campo `fim` se da para calcular?**
Para a busca de conflito ser uma consulta simples no banco
(`inicio < fim_novo` e `fim > inicio_novo`). Sem o `fim` guardado, seria preciso
trazer todos os agendamentos para o Python e calcular um por um. O custo e manter
o `fim` em dia: quando a duracao do servico muda, o `Servico.save()` recalcula o
`fim` dos agendamentos futuros (os antigos mantem o fim que tinham, o que e certo
para o historico) e o `Servico.clean()` recusa a mudanca se algum invadir outro.

**Por que um horario que so encosta no outro e aceito?**
Um corte das 10:00 as 10:30 termina exatamente quando o das 10:30 comeca. O
profissional esta livre nesse instante. Usamos `<` e `>` estritos de proposito
(ha um teste `test_horario_colado_no_fim_do_outro_e_aceito`).

**Por que cancelado nao conta como conflito?**
Um horario cancelado esta livre de novo. Se contasse, ninguem conseguiria
remarcar naquele horario.

**Por que `PROTECT` e nao `CASCADE`?**
`CASCADE` apagaria todos os agendamentos de um cliente ao excluir o cliente, sem
aviso, destruindo o historico. `PROTECT` impede e a view mostra uma mensagem.
Para servicos, a saida correta e **desativar** (campo `ativo`), nao excluir.

**Por que a exclusao so funciona por POST?**
Um link `GET` que apaga dados pode ser acionado sem querer (robo de busca,
pre-carregamento do navegador). Por isso o botao "Excluir" leva a uma tela de
confirmacao, e so o POST dela apaga. Tem teste para isso.

**Por que as views sao funcoes e nao classes?**
O Django tem *class-based views* que escrevem CRUD com menos linhas. Escolhemos
funcoes porque da para ler de cima a baixo e ver exatamente o que acontece, o
que importa mais num projeto de aprendizado.

**Por que o template `form.html` e um so para tudo?**
Porque todos os formularios tem a mesma estrutura: percorrer os campos e mostrar
os erros. O que muda (titulo, campos) vem do contexto. Evita repetir HTML.

**Por que SQLite?**
Nao exige instalar nada: quem clonar o repositorio roda na hora. A troca para
PostgreSQL mexe so no bloco `DATABASES` do `settings.py`.

**Como voce sabe que a regra funciona?**
Pelos testes automatizados (`python manage.py test`). Eles cobrem horario
sobreposto, igual, colado, cancelado e edicao do proprio agendamento.

**O que o sistema ainda nao faz?**
Nao tem login (qualquer um com o endereco mexe nos dados), nao tem paginacao nas
listas e assume um unico profissional (um horario ocupado vale para todos). Sao
os proximos passos naturais, descritos no [README](../README.md).

---

## 6. Mexa e veja

Exercicios curtos para fixar. Nenhum deles estraga o projeto.

**1. Forcar um conflito pela tela.** Crie um agendamento para amanha as 10:00
(Corte, 30 min). Tente criar outro as 10:15. Leia a mensagem. Agora tente as
10:30: deve aceitar.

**2. Ver o `fim` calculado.** No terminal, com o ambiente ativo:

```bash
python manage.py shell
```

```python
from agenda.models import Agendamento
for a in Agendamento.objects.all():
    print(a.inicio, a.fim, a.servico.duracao_minutos)
```

O `fim` e sempre o `inicio` mais a duracao.

**3. Testar a regra sem a tela.** No mesmo shell:

```python
a = Agendamento.objects.first()
print(a.conflitos())   # vazio: ele nao conflita consigo mesmo
```

**4. Quebrar de proposito.** Em `agenda/models.py`, no metodo `conflitos`,
troque `fim__gt` por `fim__gte`, rode `python manage.py test` e veja qual teste
falha (`test_horario_colado_no_fim_do_outro_e_aceito`). Desfaca a mudanca em
seguida. Isso mostra para que servem os testes: eles protegem justamente o
detalhe do `>` contra `>=`.

**5. Ver o que o banco guarda.** Abra `/admin/`, entre em Agendamentos e compare
com a tela do site. Os dois leem a mesma tabela.

**6. Proteger o historico.** Tente excluir um cliente que tem agendamento e leia
a mensagem. Depois cancele o agendamento e tente de novo (continua protegido:
cancelar nao apaga o registro; so excluir o agendamento libera o cliente).
