# Como o site funciona e como foi estruturado

Documento de **consulta**: onde fica cada coisa, o que cada endereco faz, como os
dados sao guardados e o que cada configuracao controla. Para **estudar** o codigo
passo a passo, use [ENTENDENDO-O-CODIGO.md](ENTENDENDO-O-CODIGO.md); para o cadastro de
clientes e servicos, [CADASTROS.md](CADASTROS.md); para a regra de conflito de horario em
detalhe, [AGENDAMENTO.md](AGENDAMENTO.md).

Indice: [1. Visao geral](#1-visao-geral) |
[2. Pastas](#2-estrutura-de-pastas) |
[3. Enderecos](#3-mapa-de-enderecos) |
[4. Dados](#4-modelo-de-dados) |
[5. Telas](#5-como-uma-tela-e-montada) |
[6. Validacao](#6-formularios-e-validacao) |
[7. Visual](#7-front-end-e-dependencias-externas) |
[8. Admin](#8-painel-admin) |
[9. Configuracoes](#9-configuracoes-configsettingspy) |
[10. Dados de exemplo e testes](#10-dados-de-exemplo-e-testes) |
[11. Convencoes](#11-convencoes-do-projeto) |
[12. Como acrescentar uma funcionalidade](#12-como-acrescentar-uma-funcionalidade) |
[13. Limites conhecidos](#13-limites-conhecidos)

---

## 1. Visao geral

Aplicacao web **Django** que roda em um unico processo. O navegador pede uma
pagina, o Django devolve HTML pronto (nao ha API nem JavaScript proprio):

```
Navegador --GET/POST--> config/urls.py --> agenda/urls.py --> agenda/views.py
                                                                 |      |
                                                  agenda/forms.py      agenda/models.py --> db.sqlite3
                                                                 |
                                         templates/*.html <------+  (HTML devolvido ao navegador)
```

| Camada da disciplina | Onde fica |
|---|---|
| Front-end | `templates/` e `static/css/` |
| Back-end | `agenda/urls.py`, `agenda/views.py`, `agenda/forms.py` |
| Banco de dados | `agenda/models.py`, `agenda/migrations/` e o arquivo `db.sqlite3` (criado pelo `migrate`) |

Ha **um unico app Django** (`agenda`) e uma unica pasta de configuracao (`config`).
Nao ha mais de um pacote com a mesma responsabilidade: tudo que e regra de negocio
esta em `agenda/`.

## 2. Estrutura de pastas

```
projeto/
├── manage.py                   # porta de entrada dos comandos (runserver, migrate, test...)
├── requirements.txt            # dependencias com versao fixa
├── .gitignore                  # fora do Git: .venv/, db.sqlite3, __pycache__/, .idea/, .vscode/
├── config/                     # CONFIGURACAO do projeto (nao tem regra de negocio)
│   ├── settings.py             #   todas as configuracoes (ver secao 9)
│   ├── urls.py                 #   /admin/ e entrega o resto para agenda/urls.py
│   └── wsgi.py, asgi.py        #   pontos de entrada de servidores de producao
├── agenda/                     # O APP: toda a regra de negocio
│   ├── models.py               #   Cliente, Servico, Agendamento (+ regra de conflito)
│   ├── migrations/             #   0001 (Cliente, Servico) e 0002 (Agendamento)
│   ├── forms.py                #   formularios e validacao de entrada
│   ├── views.py                #   uma funcao por tela/acao
│   ├── urls.py                 #   enderecos do site
│   ├── admin.py                #   painel /admin/ (colunas, filtros, titulo)
│   ├── tests.py                #   36 testes automatizados
│   └── management/commands/popular_dados.py   # dados de exemplo
├── templates/                  # HTML
│   ├── base.html               #   esqueleto de toda pagina do site
│   ├── agenda/                 #   telas do site (nome da pasta evita choque de nomes)
│   └── admin/base_site.html    #   so acrescenta fonte e CSS ao /admin/
├── static/css/
│   ├── estilo.css              #   visual do site (paleta, botoes, tabelas)
│   └── admin-salon.css         #   mesma paleta aplicada ao /admin/
└── docs/                       # documentacao
```

Por que existem duas pastas chamadas `agenda`: `agenda/` e o **app** (codigo Python) e
`templates/agenda/` e o **espaco de nomes dos templates** do app. E a convencao do
Django: o nome do template e `agenda/form.html`, assim dois apps nunca disputam o
mesmo nome. Sao pastas diferentes, com conteudo diferente.

## 3. Mapa de enderecos

Definidos em `agenda/urls.py` (o `config/urls.py` so entrega tudo que nao e `/admin/`).
O **apelido** (`name=`) e o que os templates e `redirect()` usam: se o endereco mudar,
nada quebra.

| Endereco | Apelido | View | Template | O que faz |
|---|---|---|---|---|
| `/` | `home` | `home` | `agenda/home.html` | Contadores e 5 proximos horarios |
| `/clientes/` | `cliente_lista` | `cliente_lista` | `agenda/cliente_lista.html` | Lista; busca `?q=` por nome ou telefone |
| `/clientes/novo/` | `cliente_novo` | `cliente_novo` | `agenda/form.html` | Cadastra |
| `/clientes/<id>/editar/` | `cliente_editar` | `cliente_editar` | `agenda/form.html` | Edita |
| `/clientes/<id>/excluir/` | `cliente_excluir` | `cliente_excluir` | `agenda/confirmar_exclusao.html` | Confirma (GET) e exclui (POST) |
| `/servicos/` | `servico_lista` | `servico_lista` | `agenda/servico_lista.html` | Lista; busca `?q=` por nome |
| `/servicos/novo/`, `/<id>/editar/`, `/<id>/excluir/` | `servico_novo`, `servico_editar`, `servico_excluir` | idem | `form.html` / `confirmar_exclusao.html` | Igual a clientes |
| `/agendamentos/` | `agendamento_lista` | `agendamento_lista` | `agenda/agendamento_lista.html` | Lista; filtros `?data=AAAA-MM-DD` e `?status=` |
| `/agendamentos/novo/`, `/<id>/editar/`, `/<id>/excluir/` | `agendamento_novo`, `agendamento_editar`, `agendamento_excluir` | idem | `form.html` / `confirmar_exclusao.html` | Igual a clientes |
| `/admin/` | (do Django) | — | `admin/...` | Painel administrativo (exige usuario) |

Regras comuns: exclusao so efetiva por **POST** (um GET so mostra a confirmacao);
`<id>` inexistente devolve a pagina "nao encontrado" (`get_object_or_404`); filtros
invalidos na URL (`?data=abc`, `?status=x`) sao ignorados em vez de quebrar a pagina.

## 4. Modelo de dados

Tres tabelas, em `agenda/models.py`. O banco e SQLite (`db.sqlite3`).

```
Cliente 1 ----< Agendamento >---- 1 Servico
```

| Tabela | Campo | Tipo | Observacao |
|---|---|---|---|
| **Cliente** | `nome` | texto (120) | obrigatorio |
| | `telefone` | texto (20) | obrigatorio |
| | `email` | e-mail | opcional |
| | `criado_em` | data/hora | automatico |
| **Servico** | `nome` | texto (120) | obrigatorio |
| | `descricao` | texto longo | opcional |
| | `duracao_minutos` | inteiro positivo | padrao 30; base do calculo do fim |
| | `preco` | decimal (8,2) | obrigatorio |
| | `ativo` | sim/nao | padrao sim; inativo some do formulario de novo agendamento |
| | `criado_em` | data/hora | automatico |
| **Agendamento** | `cliente` | FK -> Cliente | `on_delete=PROTECT` |
| | `servico` | FK -> Servico | `on_delete=PROTECT` |
| | `inicio` | data/hora | digitado pelo usuario |
| | `fim` | data/hora | **calculado** no `save()`: inicio + duracao; nao aparece no formulario |
| | `status` | agendado / concluido / cancelado | padrao agendado |
| | `observacoes` | texto longo | opcional |
| | `criado_em` | data/hora | automatico |

Ordenacao padrao: clientes e servicos por nome, agendamentos por `inicio`.
Datas ficam no banco em **UTC** e sao mostradas no fuso `America/Sao_Paulo`
(`USE_TZ = True`). Detalhes da regra de conflito: [AGENDAMENTO.md](AGENDAMENTO.md).

**Migrations** (`agenda/migrations/`): `0001_initial` cria Cliente e Servico;
`0002_agendamento` cria Agendamento. Sao arquivos gerados por `makemigrations` e
**vao para o Git**: sem elas, quem clonar nao consegue criar o banco.

## 5. Como uma tela e montada

A view prepara os dados e entrega ao template um dicionario (o *contexto*):

| View | Contexto entregue ao template |
|---|---|
| `home` | `total_clientes`, `total_servicos`, `total_agendamentos`, `proximos` (5 primeiros) |
| `*_lista` | a lista (`clientes`, `servicos` ou `agendamentos`) e o que foi digitado no filtro (`busca`, ou `data` e `status`) |
| `*_novo`, `*_editar` | `form`, `titulo` e `voltar` (apelido da lista, usado no botao Cancelar) |
| `*_excluir` | `objeto` (o que sera apagado) e `voltar` |

**Heranca de templates.** Toda pagina comeca com `{% extends "base.html" %}` e preenche
dois espacos: `{% block titulo %}` (titulo da aba) e `{% block conteudo %}`. O
`base.html` traz menu, mensagens, fontes e Bootstrap, entao eles sao escritos uma
vez so. `form.html` e `confirmar_exclusao.html` sao **genericos**: servem as tres
entidades, mudando so o contexto.

**Mensagens.** Depois de salvar ou excluir, a view chama `messages.success(...)`
(ou `messages.error(...)` quando a exclusao e bloqueada) e faz `redirect`. O
`base.html` desenha cada mensagem como `alert alert-<tag>`. Como o Bootstrap nao tem
`alert-error`, o `settings.py` traduz a tag `error` para `danger` (`MESSAGE_TAGS`,
secao 9): sem isso o aviso de erro apareceria sem cor.

## 6. Formularios e validacao

Em `agenda/forms.py`. Todos os formularios usam o `BootstrapFormMixin`, que poe a
classe do Bootstrap em cada campo (`form-control`, `form-select` para listas,
`form-check-input` para caixas), sem escrever HTML de campo a mao.

A validacao acontece em **tres niveis**, nesta ordem, e para no primeiro que falhar:

| Nivel | Onde | Exemplo |
|---|---|---|
| 1. Campo | tipo do campo no model | nome obrigatorio, e-mail valido, data no formato certo |
| 2. Formulario | `AgendamentoForm.clean_inicio` | nao marcar no passado (so se o horario foi alterado); lista de servicos so com ativos (ou o ja escolhido ao editar) |
| 3. Modelo | `Agendamento.clean()` | conflito de horario; aparece como erro geral no topo do formulario |

Por estar no nivel 3, a regra de conflito vale tambem no `/admin/`.

## 7. Front-end e dependencias externas

Nao ha build nem `npm`. O visual vem de tres fontes:

| O que | De onde | Observacao |
|---|---|---|
| Bootstrap 5.3.3 (CSS e JS) | CDN `cdn.jsdelivr.net` | **precisa de internet**; sem ela a pagina fica sem estilo |
| Fontes Fraunces (titulos) e Inter (texto) | Google Fonts | sem internet cai para Georgia e Segoe UI/Arial; o sistema continua legivel |
| `static/css/estilo.css` | arquivo do projeto | paleta vinho e dourado, botoes, tabelas, formularios |

`estilo.css` define a paleta em variaveis no topo (`--accent`, `--gold`, `--ink`,
`--bg`...) e sobrescreve as classes do Bootstrap. O logotipo da barra e um SVG
escrito direto no `base.html`.

**Cache do navegador.** Os links dos CSS terminam em `?v=` (por exemplo
`estilo.css?v=2`). Se voce alterar um CSS e o navegador continuar mostrando o antigo,
**aumente esse numero** no template. O servidor de desenvolvimento nao avisa o
navegador de que o arquivo mudou.

## 8. Painel admin

O `/admin/` e do proprio Django (cadastro completo pronto, sem escrever telas).
Personalizacoes do projeto:

| O que | Onde |
|---|---|
| Titulo "Agenda de Servicos" e "Painel administrativo" | `agenda/admin.py` (`admin.site.site_header` e outros) |
| Colunas, filtros e busca de cada tabela | classes `ClienteAdmin`, `ServicoAdmin`, `AgendamentoAdmin` em `agenda/admin.py` |
| Fontes e CSS proprios | `templates/admin/base_site.html` |
| Cores | `static/css/admin-salon.css` |

`admin-salon.css` nao refaz o layout do admin: so troca as **variaveis de cor** que o
Django ja expoe (`--primary`, `--header-bg`, `--body-bg`...). Ele precisa trocar tambem
as variaveis de texto e de fundo, porque o admin segue o tema claro/escuro do sistema
operacional; sem isso ficaria texto claro sobre fundo claro. O `base_site.html` do
projeto e uma copia do original do Django com um bloco a mais: nao da para estender o
original pelo mesmo nome (o Django entraria em laco), por isso a copia.

## 9. Configuracoes (`config/settings.py`)

| Configuracao | Valor | O que controla |
|---|---|---|
| `INSTALLED_APPS` | apps do Django + `agenda` | o que esta ligado; `agenda` registra o app |
| `MIDDLEWARE` | lista padrao | sessoes, protecao CSRF, mensagens, autenticacao (do admin) |
| `DATABASES` | SQLite em `db.sqlite3` | trocar para PostgreSQL mexe so aqui |
| `TEMPLATES` | `DIRS=[templates/]`, `APP_DIRS` | acha `templates/` da raiz e o dos apps |
| `STATIC_URL` / `STATICFILES_DIRS` | `static/` | de onde saem os CSS |
| `LANGUAGE_CODE` | `pt-br` | admin e mensagens padrao em portugues |
| `TIME_ZONE` / `USE_TZ` | `America/Sao_Paulo` / `True` | datas gravadas em UTC e mostradas no horario local; o filtro por data respeita o fuso |
| `MESSAGE_TAGS` | `error` vira `danger` | aviso de erro em vermelho (secao 5) |
| `MAILERS` | backend de console | **nenhum e-mail e enviado**: o texto aparece no terminal. E a configuracao atual do Django 6.1; `EMAIL_BACKEND` esta obsoleto |
| `SECRET_KEY` | chave de desenvolvimento | assina sessoes e formularios; **nao e segredo** neste projeto |
| `DEBUG` | `True` | mostra a pagina de erro detalhada e serve os CSS; so para desenvolvimento |
| `ALLOWED_HOSTS` | vazio | com `DEBUG=True` aceita so `localhost`/`127.0.0.1` |

**Para publicar de verdade** (entrega final), o comando
`python manage.py check --deploy` lista o que falta. Em resumo:

1. `SECRET_KEY` fora do codigo (variavel de ambiente) e `DEBUG = False`.
2. `ALLOWED_HOSTS` com o dominio do site.
3. HTTPS: `SECURE_SSL_REDIRECT`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`, `SECURE_HSTS_SECONDS`.
4. Com `DEBUG = False` o Django **para de servir os CSS**: e preciso definir `STATIC_ROOT`,
   rodar `python manage.py collectstatic` e deixar o servidor web entregar `static/`.
5. `MAILERS` com um backend real, se o sistema passar a enviar e-mail.

Em desenvolvimento esses avisos sao esperados e nao indicam erro.

## 10. Dados de exemplo e testes

**`python manage.py popular_dados`** cria 3 clientes, 3 servicos e 3 agendamentos
(amanha e depois de amanha). Rodar de novo **nao duplica**: clientes e servicos usam
`get_or_create` e os agendamentos so sao criados se ainda nao existir nenhum (os
horarios dependem do dia em que o comando roda).

**`python manage.py test`** roda 36 testes, sempre em um banco temporario:

| Grupo | Testes | Cobre |
|---|---|---|
| `ClienteTests` | 6 | cadastro, edicao, busca, nome obrigatorio, exclusao so por POST |
| `ServicoTests` | 3 | cadastro, edicao, texto da duracao |
| `HomeTests` | 2 | contador e lista de proximos; cancelado nao conta |
| `PopularDadosTests` | 1 | rodar duas vezes nao duplica |
| `AgendamentoTests` | 23 | calculo do fim; conflito (sobreposto, igual, que engloba outro, encostado nos dois lados, cancelado, reativar, editar); formulario (passado, servico inativo, erro de conflito); filtros de data e situacao, inclusive invalidos; exclusao so por POST; protecao do historico (com o aviso em vermelho); botao Cancelar |

## 11. Convencoes do projeto

- Nomes de classes, funcoes e campos em **portugues**, sem acento (`servico`, `duracao_minutos`).
- Textos da interface e dos documentos **sem acento**, de proposito (evita problema de
  codificacao ao copiar texto). Os testes procuram esses textos, entao trocar por
  acentos exige ajustar os testes.
- Uma view por acao, em **funcoes** (nao em classes): da para ler de cima a baixo.
- Regra de negocio no **model**, nao na view, para valer em qualquer lugar que salve.
- Cada migration gerada por `makemigrations` e commitada junto com a mudanca do model.

## 12. Como acrescentar uma funcionalidade

Receita, na ordem em que as camadas se encaixam:

1. **Model** em `agenda/models.py` (e a regra, se houver, no metodo `clean()`).
2. `python manage.py makemigrations` e `python manage.py migrate`.
3. **Formulario** em `agenda/forms.py` (herdando de `BootstrapFormMixin` e `ModelForm`).
4. **View(s)** em `agenda/views.py` e **enderecos** em `agenda/urls.py` (com `name=`).
5. **Template** em `templates/agenda/` (`{% extends "base.html" %}`) e um link no menu do `base.html`.
6. Registrar no **admin** em `agenda/admin.py`.
7. **Testes** em `agenda/tests.py`, incluindo o caso de erro.
8. Atualizar a documentacao (esta pagina, `AGENDAMENTO.md` ou um documento novo).

**Repeticao conhecida.** As views de cadastrar e editar de cliente, servico e
agendamento tem a mesma estrutura (cerca de dois tercos de `views.py` e CRUD). Foi uma
escolha: cada view se le inteira, o que ajuda a explicar o projeto. Quando surgir uma
quarta entidade, vale trocar por um auxiliar unico ou pelas *class-based views*
(`CreateView`/`UpdateView`) do Django, que reduzem isso a poucas linhas; os testes
garantem que nada muda por fora.

## 13. Limites conhecidos

- **Sem login**: qualquer pessoa com o endereco altera os dados (`login_required` e o passo natural).
- **Um unico profissional**: um horario ocupado vale para toda a agenda.
- **Duracao do servico alterada depois** nao atualiza o `fim` dos agendamentos futuros ja gravados.
- **Preco negativo** e aceito pelo formulario de servico; duracao 0 tambem (a regra de conflito ainda protege o meio de um horario ocupado, mas nao as bordas).
- **Sem paginacao** nas listas.
- A checagem de conflito e feita antes de gravar, **sem trava no banco**: dois envios no mesmo instante poderiam passar. Para um uso local isso nao importa; um sistema real precisaria de uma restricao no banco.
- **Depende de internet** para Bootstrap e fontes.
