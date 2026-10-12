# Funcionalidade: Agendamento

Esta e a segunda funcionalidade do projeto. Ela liga os dois cadastros que ja
existiam, **Cliente** e **Servico**, e permite **marcar um horario**. A regra
principal e simples de dizer:

> **Dois agendamentos nao podem ocupar o mesmo horario.**

Este documento explica o que a funcionalidade faz, como o codigo foi organizado
e por que cada decisao foi tomada. Leia na ordem: as secoes 1 a 3 mostram *o que*
ela faz; da 4 em diante mostram *como*.

## Indice

1. [Visao rapida](#1-visao-rapida)
2. [Como usar (passo a passo)](#2-como-usar-passo-a-passo)
3. [Regras de negocio](#3-regras-de-negocio)
4. [Modelo de dados](#4-modelo-de-dados)
5. [Como o conflito de horario e detectado](#5-como-o-conflito-de-horario-e-detectado)
6. [O caminho de um pedido: criar um agendamento](#6-o-caminho-de-um-pedido-criar-um-agendamento)
7. [Onde esta cada coisa](#7-onde-esta-cada-coisa)
8. [Decisoes tecnicas e por que foram tomadas](#8-decisoes-tecnicas-e-por-que-foram-tomadas)
9. [Testes](#9-testes)
10. [Limitacoes conhecidas](#10-limitacoes-conhecidas)
11. [Como estender](#11-como-estender)

---

## 1. Visao rapida

| Pergunta | Resposta |
|---|---|
| O que e um agendamento? | Um **cliente** marcou um **servico** em um **horario** |
| Como o horario termina? | O sistema calcula: `fim = inicio + duracao do servico` |
| O que o sistema impede? | Dois horarios sobrepostos |
| O que o usuario informa? | Cliente, servico, inicio, situacao e observacoes |
| Onde fica? | Menu **Agendamentos** (`/agendamentos/`) e o painel inicial |

```
Cliente 1 ----< Agendamento >---- 1 Servico
```

Um cliente pode ter varios agendamentos, e um servico pode aparecer em varios
agendamentos.

---

## 2. Como usar (passo a passo)

Para ter dados de exemplo antes de testar:

```bash
python manage.py popular_dados
```

### 2.1 Telas

| Tela | Endereco | O que faz |
|---|---|---|
| Lista | `/agendamentos/` | Mostra os horarios; filtra por **data** e por **situacao** |
| Novo | `/agendamentos/novo/` | Marca um horario |
| Editar | `/agendamentos/<id>/editar/` | Muda cliente, servico, horario ou situacao (a situacao so aparece na edicao; todo agendamento novo nasce "agendado") |
| Excluir | `/agendamentos/<id>/excluir/` | Apaga, depois de uma tela de confirmacao |

O **painel inicial** (`/`) mostra quantos agendamentos futuros existem e os 5
proximos horarios.

### 2.2 Exemplo: marcar um horario

1. Em **Agendamentos**, clique em **Novo agendamento**.
2. Escolha o cliente e o servico (ex.: *Corte de cabelo*, 30 min).
3. Escolha o inicio, ex.: **amanha as 09:00**.
4. Clique em **Salvar**. A lista mostra `09:00 - 09:30`: o fim foi calculado.

### 2.3 Exemplo: ver o conflito

Com o agendamento acima criado, tente marcar outro **amanha as 09:15**:

```
Horario indisponivel: ja existe Corte de cabelo para Maria Silva das 09:00 as 09:30 (10/10/2026).
```

O formulario volta com o que foi digitado e nada e gravado. Agora tente
**09:30**: e aceito, porque o primeiro termina exatamente quando o segundo comeca.

### 2.4 Outras situacoes que voce vai ver

| Situacao | O que acontece |
|---|---|
| Data no passado ao criar | `Escolha uma data e hora no futuro.` |
| Excluir cliente com agendamento | `Nao e possivel excluir: o cliente possui agendamentos.` |
| Excluir servico com agendamento | `Nao e possivel excluir: o servico possui agendamentos. Desative-o em vez de excluir.` |
| Marcar como **Cancelado** | O horario fica livre de novo |
| Servico **inativo** | Nao aparece para novos agendamentos |

---

## 3. Regras de negocio

| # | Regra | Onde e garantida |
|---|---|---|
| R1 | O fim do agendamento e `inicio + duracao_minutos` do servico | `Agendamento.save()` |
| R2 | Dois agendamentos nao podem se sobrepor | `Agendamento.clean()` |
| R3 | Horarios que apenas se encostam (um termina quando o outro comeca) sao permitidos | `Agendamento.conflitos()` |
| R4 | Agendamento **cancelado** nao ocupa horario | `Agendamento.conflitos()` |
| R5 | Nao se cria agendamento no passado | `AgendamentoForm.clean_inicio()` |
| R6 | Agendamento antigo pode ser editado (ex.: marcar como concluido) sem mudar o horario | `AgendamentoForm.clean_inicio()` |
| R7 | Servico inativo nao pode ser escolhido para um novo agendamento | `AgendamentoForm.__init__()` |
| R8 | Cliente ou servico com agendamento nao pode ser excluido | `on_delete=PROTECT` + views |
| R9 | Reativar um agendamento cancelado volta a checar conflito | `Agendamento.clean()` |
| R10 | Trocar o servico de um agendamento tambem checa conflito, com a nova duracao | `Agendamento.clean()` |

---

## 4. Modelo de dados

Classe `Agendamento`, em `agenda/models.py`.

| Campo | Tipo | Observacao |
|---|---|---|
| `cliente` | chave estrangeira para `Cliente` | `PROTECT`; acesso reverso `cliente.agendamentos` |
| `servico` | chave estrangeira para `Servico` | `PROTECT`; acesso reverso `servico.agendamentos` |
| `inicio` | data e hora | informado pelo usuario |
| `fim` | data e hora | **calculado**, nao aparece no formulario (`editable=False`) |
| `status` | texto com opcoes | `agendado` (padrao), `concluido`, `cancelado` |
| `observacoes` | texto | opcional |
| `criado_em` | data e hora | preenchido automaticamente |

Na lista, os horarios que ainda vao acontecer aparecem primeiro (do mais proximo
para o mais distante), seguidos dos que ja passaram (do mais recente para o mais
antigo). A ordem e montada em `agendamento_lista` (`views.py`); no model, a
ordenacao padrao continua sendo por `inicio`.

---

## 5. Como o conflito de horario e detectado

### 5.1 A ideia

Dois horarios **se sobrepoem** quando **cada um comeca antes do outro terminar**.

```
existente:    |---------|             10:00 - 10:30

novo A:           |---------|         10:15 - 10:45   CONFLITO
novo B:                     |------|  10:30 - 11:00   OK  (so encosta)
novo C:   |--------------------|      09:45 - 10:15   CONFLITO
novo D:  |-------------------------|  09:00 - 11:00   CONFLITO (engloba o existente)
```

### 5.2 Em tabela

Considere um existente de `10:00` ate `10:30`.

| Novo horario | Comeca antes das 10:30? | Termina depois das 10:00? | Resultado |
|---|---|---|---|
| 10:15 - 10:45 | sim | sim | **conflito** |
| 10:30 - 11:00 | **nao** (e igual) | sim | livre |
| 09:30 - 10:00 | sim | **nao** (e igual) | livre |
| 09:45 - 10:15 | sim | sim | **conflito** |
| 09:00 - 11:00 | sim | sim | **conflito** |

### 5.3 No codigo

```python
def conflitos(self):
    return (
        Agendamento.objects
        .exclude(status=self.Status.CANCELADO)    # cancelado nao ocupa horario
        .exclude(pk=self.pk)                      # nao conflita consigo mesmo
        .filter(inicio__lt=self.calcular_fim(),   # outro comeca antes deste terminar
                fim__gt=self.inicio)              # outro termina depois deste comecar
    )
```

Leia como uma frase: *"agendamentos que nao estejam cancelados, que nao sejam
este mesmo, que comecem antes de este terminar e terminem depois de este comecar"*.

O detalhe mais importante e usar `<` e `>` **estritos** (`lt` e `gt`). Com `<=`
e `>=`, horarios que so se encostam seriam recusados sem necessidade.

### 5.4 Onde a regra e aplicada

O metodo `clean()` do model chama `conflitos()` e, se achar algum, levanta
`ValidationError` com a mensagem "Horario indisponivel...". Como o `clean()` e
chamado por `form.is_valid()`, o erro volta para a tela sem nenhum codigo extra
na view.

---

## 6. O caminho de um pedido: criar um agendamento

```
Navegador          urls.py              views.py              forms.py            models.py        banco
   |                  |                     |                     |                   |               |
   |-- GET  novo/ --->|-- agendamento_novo ->| AgendamentoForm() ->|                   |               |
   |<------- tela com o formulario vazio ----|                     |                   |               |
   |                                                                                                    |
   |-- POST novo/ --->|-- agendamento_novo ->| is_valid() -------->| clean_inicio()    |               |
   |                  |                     |                     |  (data futura?)   |               |
   |                  |                     |                     |-----------------> | clean()       |
   |                  |                     |                     |                   |  (conflito?)  |
   |                  |                     |<--- valido ---------|                   |               |
   |                  |                     | save() -------------------------------> | calcula fim ->| INSERT
   |<--- redirect para a lista + mensagem ---|                     |                   |               |
```

Passo a passo:

1. **`GET /agendamentos/novo/`** chega em `agendamento_novo`. Sem dados enviados,
   o formulario nasce vazio e a tela e desenhada por `templates/agenda/form.html`.
2. O usuario preenche e envia (**`POST`**). A mesma view monta o formulario com os
   dados recebidos e chama `form.is_valid()`.
3. A validacao acontece em tres niveis:
   - **Campo:** tipos e obrigatoriedade (ex.: inicio e uma data valida).
   - **Formulario:** `clean_inicio()` recusa data no passado.
   - **Model:** `clean()` recusa conflito de horario.
4. Se algum nivel falhar, a view mostra a tela de novo com os erros e o que foi
   digitado. Nada e gravado.
5. Se tudo passar, `form.save()` chama `Agendamento.save()`, que calcula o `fim`
   e grava.
6. A view guarda uma mensagem de sucesso e faz **redirect** para a lista. O
   redirect evita que apertar F5 reenvie o formulario e crie um duplicado.

---

## 7. Onde esta cada coisa

| Camada | Arquivo | O que tem la |
|---|---|---|
| Dados | `agenda/models.py` | Classe `Agendamento`, calculo do fim, regra de conflito |
| Dados | `agenda/migrations/0002_agendamento.py` | Cria a tabela no banco |
| Back-end | `agenda/forms.py` | `AgendamentoForm`: widget de data, servicos ativos, data futura |
| Back-end | `agenda/views.py` | `agendamento_lista`, `_novo`, `_editar`, `_excluir`; contadores da `home` |
| Back-end | `agenda/urls.py` | Os 4 enderecos de `/agendamentos/` |
| Front-end | `templates/agenda/agendamento_lista.html` | Tabela com filtros e etiquetas de situacao |
| Front-end | `templates/agenda/form.html` | Formulario generico (mostra o erro de conflito) |
| Front-end | `templates/agenda/home.html` | Contador e proximos horarios |
| Admin | `agenda/admin.py` | `AgendamentoAdmin` (a regra de conflito vale aqui tambem) |
| Dados de exemplo | `agenda/management/commands/popular_dados.py` | Cria 3 agendamentos se nao houver nenhum |
| Testes | `agenda/tests.py` | Classe `AgendamentoTests` |

---

## 8. Decisoes tecnicas e por que foram tomadas

**O `fim` e guardado no banco, em vez de calculado so quando necessario.**
Com o `fim` gravado, procurar conflitos vira uma consulta simples e o proprio
banco faz o filtro. Sem ele, seria preciso trazer todos os agendamentos para o
Python e calcular um a um. Para o `fim` nao ficar desatualizado, quando a
duracao de um servico muda o `Servico.save()` recalcula o `fim` dos agendamentos
**futuros** dele; os que ja aconteceram mantem o fim que tinham (historico). Se o
novo fim invadir outro horario, `Servico.clean()` recusa a mudanca.

**A regra de conflito fica no model (`clean()`), nao na view.**
O model e o ponto por onde todo salvamento com validacao passa. Se a regra
estivesse na view, o painel `/admin/` (que nao usa as views do projeto) poderia
criar horarios conflitantes. No model, ela vale nos dois lugares.

**`PROTECT` nas chaves estrangeiras.**
Com `CASCADE`, excluir um cliente apagaria o historico dele sem aviso. Com
`PROTECT`, o Django impede, e as views `cliente_excluir` e `servico_excluir`
capturam o `ProtectedError` para mostrar uma mensagem amigavel. Para tirar um
servico de uso, o caminho correto e desativa-lo (campo `ativo`).

**Cancelado nao e excluido: e uma situacao.**
Manter o registro como `cancelado` preserva o historico e libera o horario. Quem
quiser apagar de vez usa **Excluir**.

**Validacao da data futura so quando o horario muda.**
Se a regra valesse sempre, nao seria possivel marcar um atendimento antigo como
`concluido`. Por isso `clean_inicio()` so recusa o passado em agendamento novo ou
quando o campo `inicio` foi alterado.

**`type="datetime-local"` no campo de inicio.**
O navegador mostra um seletor de data e hora pronto, sem JavaScript. O formato
enviado (`AAAA-MM-DDTHH:MM`) foi declarado em `input_formats`.

**Views em funcao, como no resto do projeto.**
Mantem o mesmo estilo dos cadastros de cliente e servico: da para ler cada tela
de cima a baixo.

---

## 9. Testes

```bash
python manage.py test
```

O projeto tem **44 testes**; **32** sao de agendamento (classe `AgendamentoTests`).
A tabela mostra o que cada um garante.

| Regra | Teste |
|---|---|
| R1 | `test_fim_e_inicio_mais_duracao_do_servico` |
| R2 | `test_horario_sobreposto_e_recusado`, `test_mesmo_horario_e_recusado`, `test_horario_que_engloba_outro_e_recusado` |
| R2 (na tela) | `test_formulario_mostra_erro_de_conflito_e_nao_salva`, `test_editar_para_dentro_de_outro_horario_e_recusado` |
| R3 | `test_horario_colado_no_fim_do_outro_e_aceito`, `test_horario_colado_no_inicio_do_outro_e_aceito` |
| R4 | `test_agendamento_cancelado_libera_o_horario` |
| R5 | `test_formulario_recusa_data_no_passado` |
| R6 | `test_agendamento_antigo_pode_ser_marcado_como_concluido` |
| R7 | `test_servico_inativo_nao_aparece_no_formulario_novo` |
| R8 | `test_cliente_com_agendamento_nao_pode_ser_excluido`, `test_servico_com_agendamento_nao_pode_ser_excluido` |
| R9 | `test_reativar_agendamento_cancelado_volta_a_checar_conflito` |
| R10 | `test_trocar_para_servico_mais_longo_que_invade_o_proximo_e_recusado` |
| Editar sem conflitar consigo | `test_editar_sem_mudar_horario_nao_conflita_consigo_mesmo` |
| Criar pela tela | `test_cadastra_agendamento_pelo_formulario` |
| Lista e filtros | `test_lista_filtra_por_data`, `test_lista_filtra_por_situacao`, `test_lista_ignora_filtros_invalidos` |
| Exclusao so por POST | `test_get_na_exclusao_nao_apaga_o_agendamento`, `test_post_na_exclusao_apaga_o_agendamento` |
| Botao Cancelar | `test_cancelar_do_formulario_volta_para_a_lista` |
| Duracao minima do servico | `test_servico_com_duracao_zero_e_recusado` |
| Mudar a duracao do servico | `test_mudar_duracao_recalcula_o_fim_dos_agendamentos_futuros`, `test_mudar_duracao_nao_mexe_em_agendamento_passado`, `test_mudar_duracao_que_invade_outro_horario_e_recusado` |
| Situacao so na edicao | `test_formulario_novo_nao_mostra_o_campo_situacao`, `test_agendamento_novo_sempre_nasce_agendado`, `test_formulario_de_edicao_mantem_o_campo_situacao` |
| Ordem da lista | `test_lista_mostra_primeiro_o_horario_mais_proximo` |

**Experimento para ver os testes funcionando:** em `agenda/models.py`, no metodo
`conflitos`, troque `fim__gt` por `fim__gte`, rode os testes e veja
`test_horario_colado_no_fim_do_outro_e_aceito` falhar. Desfaca a troca em seguida.

---

## 10. Limitacoes conhecidas

Resultado da revisao do codigo. Nenhuma delas e um defeito para o escopo do
trabalho, mas e bom conhecer. (A duracao 0, a situacao na criacao, a ordem da
lista e o `fim` desatualizado apos mudar a duracao do servico apareceram em uma
revisao anterior e ja foram corrigidos.)

| Limitacao | Detalhe | Como seria resolvida |
|---|---|---|
| **Um unico profissional** | Um horario ocupado vale para toda a agenda; dois clientes nao podem ser atendidos ao mesmo tempo | Campo `profissional` no model e conflito calculado por profissional |
| **Corrida entre dois envios simultaneos** | A checagem e o `save()` nao sao atomicos: dois pedidos no mesmo instante poderiam passar juntos | Transacao com bloqueio (`select_for_update`) ou restricao no banco |
| **`objects.create()` nao valida** | Criar pelo codigo (como faz o `popular_dados`) nao executa `clean()`; so formulario e admin validam | Chamar `full_clean()` antes, ou validar em `save()` |
| **Lista sem paginacao** | Todos os horarios aparecem juntos (os mais proximos primeiro) | Paginacao |
| **Sem login** | Qualquer pessoa com o endereco altera os dados | Autenticacao e `login_required` |

---

## 11. Como estender

**Adicionar um campo (ex.: `valor_cobrado`):**
1. Acrescente o campo em `Agendamento` (`agenda/models.py`).
2. Rode `python manage.py makemigrations` e depois `python manage.py migrate`.
3. Inclua o campo em `fields` do `AgendamentoForm`.
4. Mostre-o em `agendamento_lista.html`.
5. Escreva um teste em `AgendamentoTests`.

**Mudar a regra (ex.: intervalo minimo de 10 minutos entre atendimentos):**
Altere apenas `calcular_fim()` ou o filtro em `conflitos()`, em `models.py`. A
regra esta concentrada ali e os testes de conflito mostram o que quebrou.

**Adicionar profissional:** acrescente a chave estrangeira em `Agendamento`, filtre
`conflitos()` por `profissional=self.profissional` e inclua o campo no formulario.
