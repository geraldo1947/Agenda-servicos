# Explicando a implementacao

Guia para quem precisa **explicar a outra pessoa** (colega, cliente, professor)
o que a branch `feature/agendamento` entregou. Ele parte do que realmente mudou
na branch em relacao a `main` e sugere uma ordem de explicacao.

Para o detalhe tecnico completo da funcionalidade, veja
[AGENDAMENTO.md](AGENDAMENTO.md). Este documento e o "como contar a historia".

## Indice

1. [Em 30 segundos e em 2 minutos](#1-em-30-segundos-e-em-2-minutos)
2. [O tamanho da mudanca](#2-o-tamanho-da-mudanca)
3. [Os 6 commits, um por um](#3-os-6-commits-um-por-um)
4. [Arquivo por arquivo: o que mudou e por que](#4-arquivo-por-arquivo-o-que-mudou-e-por-que)
5. [O que e agendamento e o que e "correcao de passagem"](#5-o-que-e-agendamento-e-o-que-e-correcao-de-passagem)
6. [Roteiro de explicacao (ordem sugerida)](#6-roteiro-de-explicacao-ordem-sugerida)
7. [Demonstracao de 5 minutos](#7-demonstracao-de-5-minutos)
8. [Perguntas que podem aparecer](#8-perguntas-que-podem-aparecer)
9. [O que nao afirmar](#9-o-que-nao-afirmar)
10. [Como conferir tudo sozinho](#10-como-conferir-tudo-sozinho)

---

## 1. Em 30 segundos e em 2 minutos

**30 segundos**

> "Ate aqui o sistema cadastrava clientes e servicos. Esta branch acrescenta o
> **agendamento**: marcar um servico para um cliente em um horario. O sistema
> calcula quando termina, somando a duracao do servico, e **nao deixa dois
> agendamentos ocuparem o mesmo horario**."

**2 minutos**

> "O agendamento liga as duas coisas que ja existiam: um cliente e um servico.
> O usuario informa so o inicio; o fim e calculado pela duracao do servico.
>
> A regra principal e o conflito de horario: se o novo horario se sobrepoe a um
> que ja existe, o sistema recusa e mostra qual horario esta ocupado. Horarios
> que apenas se encostam, como 10:00 a 10:30 e 10:30 a 11:00, sao permitidos, e
> agendamentos cancelados liberam o horario.
>
> Essa regra esta no model, e nao na tela, entao vale tambem no painel
> administrativo. Alem disso, cliente ou servico que ja tem agendamento nao
> podem ser excluidos, para nao perder o historico. Tudo isso tem testes
> automatizados."

---

## 2. O tamanho da mudanca

| Medida | Valor |
|---|---|
| Commits | 6 |
| Arquivos | 15 nos 6 commits (12 existentes alterados e 3 novos), mais este guia |
| Linhas | 1076 adicionadas e 37 removidas |
| Testes | de 5 para **36** (31 novos) |
| Tabela nova no banco | `agenda_agendamento` (migration `0002`) |
| Telas novas | lista, novo, editar e excluir agendamentos |
| Telas alteradas | painel inicial, menu e formulario generico |

Boa parte das linhas e teste e documentacao. O codigo de producao novo e
pequeno: o model ganhou 77 linhas e as views tiveram 97 linhas alteradas.

---

## 3. Os 6 commits, um por um

Cada commit deixa o sistema funcionando. Dizer isso e um bom argumento de
organizacao.

| # | Commit | O que entrega | Frase para explicar |
|---|---|---|---|
| 1 | `ab17580` Corrige EMAIL_BACKEND e a cor das mensagens de erro | `config/settings.py` | "Preparacao: mensagens de erro em vermelho e comentarios de configuracao. (A troca de MAILERS por EMAIL_BACKEND feita aqui foi um engano e foi revertida depois; veja a secao 5.)" |
| 2 | `304625b` Adiciona model Agendamento com regra de conflito de horario | `models.py`, migration `0002`, `admin.py` | "Aqui nasce a funcionalidade: a tabela e a regra de conflito." |
| 3 | `8649842` Adiciona telas de agendamento e protege cliente/servico com agendamento | `forms.py`, `views.py`, `urls.py`, templates, `popular_dados.py` | "Aqui o usuario passa a usar: telas, filtros, painel e a protecao contra excluir quem tem agendamento." |
| 4 | `f5a11d0` Adiciona testes de agendamento e cobre lacunas | `tests.py` | "A prova de que a regra funciona, incluindo os casos de borda." |
| 5 | `3f568dd` Testa troca para servico mais longo que invade o proximo | `tests.py` | "Um caso especifico: editar para um servico mais longo tambem checa conflito." |
| 6 | `129155e` Documenta a funcionalidade de agendamento | `README.md`, `docs/AGENDAMENTO.md` | "Documentacao para quem for manter o codigo." |

---

## 4. Arquivo por arquivo: o que mudou e por que

### 4.1 Novos

| Arquivo | O que e | Por que existe |
|---|---|---|
| `agenda/migrations/0002_agendamento.py` | Cria a tabela de agendamentos | O Django guarda no banco mudancas em `models.py` por migration |
| `templates/agenda/agendamento_lista.html` | Tela da lista, com filtros e etiquetas de situacao | E a tela principal da funcionalidade |
| `docs/AGENDAMENTO.md` | Documentacao tecnica da funcionalidade | Registrar regras, decisoes e limites |
| `docs/EXPLICANDO-A-IMPLEMENTACAO.md` | Este guia | Ajudar a explicar o que foi feito |

### 4.2 Alterados: o nucleo da funcionalidade

| Arquivo | O que mudou | Por que |
|---|---|---|
| `agenda/models.py` | Nova classe `Agendamento`: campos, `calcular_fim()`, `conflitos()`, `clean()`, `save()` | **O coracao.** A regra de negocio fica aqui para valer em qualquer lugar |
| `agenda/forms.py` | `AgendamentoForm`: seletor de data/hora, so servicos ativos, recusa data passada | Validacoes da tela. Tambem os selects passam a usar o estilo `form-select` |
| `agenda/views.py` | 4 views de agendamento; `home` com contador e proximos horarios | O que acontece em cada endereco |
| `agenda/urls.py` | 4 enderecos novos em `/agendamentos/` | Ligar enderecos as views |
| `agenda/admin.py` | `AgendamentoAdmin` | A funcionalidade tambem aparece no `/admin/` |

### 4.3 Alterados: ajustes de apoio

| Arquivo | O que mudou | Por que |
|---|---|---|
| `templates/base.html` | Link "Agendamentos" no menu; link do admin por `{% url %}` | Navegacao |
| `templates/agenda/home.html` | Terceiro contador e lista de proximos horarios | Visao geral no painel inicial |
| `templates/agenda/form.html` | Mostra o erro geral do formulario; "Cancelar" volta para a lista | O erro de conflito nao pertence a um campo e nao aparecia |
| `agenda/management/commands/popular_dados.py` | Cria 3 agendamentos de exemplo, sem duplicar | Demonstrar sem digitar tudo |
| `config/settings.py` | `MESSAGE_TAGS` e comentarios; `MAILERS` mantido | Ver secao 5 |
| `agenda/tests.py` | +31 testes | Garantir o comportamento |
| `README.md` | Funcionalidades, estrutura e decisoes atualizadas | Manter a documentacao em dia |

---

## 5. O que e agendamento e o que e "correcao de passagem"

Para nao confundir quem ouve, separe o que **e** a funcionalidade do que foi
**ajustado no caminho**.

**E a funcionalidade de agendamento**
- Model, migration, admin, formulario, views, urls, templates de lista e home.
- A regra de conflito e o calculo do fim.
- A protecao de cliente e servico com agendamento.

**Ajustes feitos de passagem (nao sao agendamento)**
| Ajuste | Onde | Motivo |
|---|---|---|
| `MAILERS` mantido (uma troca por `EMAIL_BACKEND` foi feita e **revertida**) | `settings.py` | `MAILERS` e a configuracao atual do Django 6.1; `EMAIL_BACKEND` esta deprecada para o Django 7.0. A troca do commit `ab17580` foi um engano, corrigido depois |
| `MESSAGE_TAGS` | `settings.py` | O Bootstrap nao tem `alert-error`; sem isso o aviso de erro aparecia sem cor |
| Botao "Cancelar" corrigido | `form.html` e views de formulario | Depois de um erro, ele apontava para o proprio formulario |
| `ProtectedError` tratado | `cliente_excluir` e `servico_excluir` | Sem tratar, excluir quem tem agendamento daria erro 500 |
| Admin por `{% url %}` | `base.html` | Evitar endereco escrito a mao |

Dizer isso explicitamente passa seguranca: mostra que voce sabe o que cada linha
faz.

---

## 6. Roteiro de explicacao (ordem sugerida)

Para uma explicacao de uns 10 minutos. Cada passo diz o que abrir.

| # | Tempo | Mostrar | O que dizer |
|---|---|---|---|
| 1 | 1 min | Este guia, secao 1 | O que a funcionalidade faz, em duas frases |
| 2 | 1 min | `git log --oneline origin/main..feature/agendamento` | Seis commits, cada um com uma ideia |
| 3 | 3 min | `agenda/models.py`, classe `Agendamento` | Campos, `fim` calculado, e o metodo `conflitos()` explicado com a linha do tempo |
| 4 | 1 min | `agenda/forms.py` | As tres validacoes (campo, formulario, model) |
| 5 | 1 min | `agenda/views.py`, `agendamento_novo` | A view e curta: o trabalho pesado esta no model e no form |
| 6 | 2 min | Sistema rodando | A demonstracao da secao 7 |
| 7 | 1 min | `python manage.py test` | 36 testes, todos passando |

**Para explicar `conflitos()` sem se perder**, desenhe isto:

```
existente:    |---------|             10:00 - 10:30
novo A:           |---------|         10:15 - 10:45   CONFLITO
novo B:                     |------|  10:30 - 11:00   OK (so encosta)
```

E diga: *"conflita quando cada um comeca antes do outro terminar. Por isso uso
menor e maior estritos."*

---

## 7. Demonstracao de 5 minutos

Preparar:

```bash
python manage.py migrate
python manage.py popular_dados
python manage.py runserver
```

O `popular_dados` cria *Maria Silva, Corte de cabelo, amanha as 09:00*.

| # | Acao | O que acontece | O que dizer |
|---|---|---|---|
| 1 | Abrir `/` | Contador e proximos horarios | "O painel ja mostra o que vem por ai" |
| 2 | **Agendamentos** → ver a lista | `09:00 - 09:30` | "O fim foi calculado pela duracao" |
| 3 | **Novo agendamento**, Joao, Corte, amanha **09:15** | Erro vermelho: horario indisponivel | "Recusou e disse qual horario esta ocupado" |
| 4 | Mudar para **09:30** e salvar | Aceito | "Encostar e permitido" |
| 5 | Editar o primeiro → **Cancelado** | Horario livre de novo | "Cancelado nao ocupa horario" |
| 6 | **Clientes** → excluir Maria | Mensagem: possui agendamentos | "Protege o historico" |
| 7 | **Novo agendamento** com data de ontem | Erro: escolha data futura | "Nao se agenda no passado" |

---

## 8. Perguntas que podem aparecer

**Por que o `fim` e guardado se da para calcular?**
Para o banco fazer a busca de conflito sozinho, com uma consulta simples. Se a
duracao do servico mudar depois, os agendamentos antigos mantem o fim que
tinham, o que e o certo para historico.

**Por que a regra esta no model e nao na view?**
Porque o model e por onde todo salvamento com validacao passa. Na view, o
`/admin/` poderia criar horarios conflitantes. (Foi verificado: o admin aplica a
regra.)

**Por que horarios colados sao aceitos?**
Um termina exatamente quando o outro comeca; o profissional esta livre naquele
instante. Ha testes para os dois lados (`..._colado_no_fim_...` e
`..._colado_no_inicio_...`).

**Por que cancelado libera o horario?**
Senao ninguem poderia remarcar. E o registro continua no historico.

**O que acontece se duas pessoas marcarem o mesmo horario ao mesmo tempo?**
Em teoria os dois podem passar, porque a checagem e o salvamento nao sao
atomicos. E uma limitacao conhecida (secao 9) e a solucao seria uma transacao
com bloqueio ou uma restricao no banco.

**O sistema serve para mais de um profissional?**
Nao. Um horario ocupado vale para toda a agenda. Para varios profissionais,
seria preciso um campo `profissional` e calcular o conflito por profissional.

**O que e a migration?**
E o arquivo que descreve a mudanca no banco (criar a tabela `agendamento`).
Quem baixar o projeto roda `python manage.py migrate` e a tabela e criada.

**Por que `PROTECT` e nao `CASCADE`?**
`CASCADE` apagaria os agendamentos junto com o cliente, sem aviso. `PROTECT`
impede, e a tela explica o motivo.

**Por que alguns arquivos nao tem relacao direta com agendamento?**
Foram ajustes de passagem (secao 5): configuracao de e-mail, cor das mensagens
de erro e o botao Cancelar.

---

## 9. O que nao afirmar

Para nao prometer mais do que o sistema faz:

| Nao diga | Diga |
|---|---|
| "Impede qualquer conflito" | "Impede conflito em uso normal; dois envios simultaneos podem passar" |
| "Suporta varios profissionais" | "Hoje e uma agenda unica" |
| "Tem controle de acesso" | "Nao tem login; qualquer um com o endereco altera os dados" |
| "Valida tudo em qualquer caminho" | "Valida pelo formulario e pelo admin; `objects.create()` direto no codigo nao executa a validacao" |
| "Esta pronto para producao" | "E um projeto academico: `DEBUG` ligado e SQLite" |

A lista completa de limitacoes esta em [AGENDAMENTO.md](AGENDAMENTO.md#10-limitacoes-conhecidas).

---

## 10. Como conferir tudo sozinho

Com o repositorio clonado e a branch baixada:

```bash
git fetch origin
git switch feature/agendamento
```

**Ver o que mudou**

```bash
git log --oneline origin/main..feature/agendamento       # os commits
git diff --stat origin/main..feature/agendamento         # arquivos e tamanho
git diff origin/main..feature/agendamento -- agenda/models.py   # um arquivo
git show 304625b                                         # um commit inteiro
```

**Ver quem fez cada commit**

```bash
git log --format="%h %an | %s" origin/main..feature/agendamento
```

Cada mensagem de commit registra a coautoria; se perguntarem como foi feito,
responda direto com base nisso.

**Rodar e testar**

```bash
python manage.py migrate
python manage.py test        # deve terminar com: Ran 36 tests ... OK
python manage.py popular_dados
python manage.py runserver
```

**Experimento que impressiona e e facil de explicar**

Em `agenda/models.py`, no metodo `conflitos`, troque `fim__gt` por `fim__gte`,
rode `python manage.py test` e mostre que
`test_horario_colado_no_fim_do_outro_e_aceito` passa a falhar. Desfaca a troca
depois (`git restore agenda/models.py`). Isso mostra que a regra esta protegida
por teste.
