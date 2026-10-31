# Agenda de Servicos

Sistema web de agendamento de servicos (barbearia / salao / clinica), feito em
**Python + Django** para a materia de Projeto de Software.

Funcionalidades:

- **Clientes**: cadastro, busca por nome ou telefone, edicao e exclusao.
- **Servicos**: cadastro com duracao e preco, busca, edicao e exclusao.
  Detalhes dos dois cadastros em [`docs/CADASTROS.md`](docs/CADASTROS.md).
- **Agendamentos**: marcar horario para um cliente e um servico, com filtro por
  data e situacao. O sistema **bloqueia horarios em conflito**, calculando o fim
  de cada agendamento pela duracao do servico (detalhes em
  [`docs/AGENDAMENTO.md`](docs/AGENDAMENTO.md)).
- **Relatorios**: faturamento (so agendamentos concluidos), valor a receber,
  taxa de cancelamento e rankings de servicos e clientes, por periodo
  (detalhes em [`docs/RELATORIOS.md`](docs/RELATORIOS.md)).
- **Painel inicial** com contadores e os proximos horarios.
- **Painel `/admin/`** do Django, personalizado.

Atende o requisito de **3 camadas**:

| Camada | Onde fica |
|---|---|
| Front-end | `templates/` + `static/css/` (HTML dos templates Django + Bootstrap 5) |
| Back-end | `agenda/views.py`, `agenda/forms.py`, `agenda/urls.py` |
| Banco de dados | `agenda/models.py` + migrations (SQLite no desenvolvimento) |

## Como rodar

Precisa de **Python 3.12 ou mais novo** instalado.

```bash
git clone https://github.com/geraldo1947/Agenda-servicos.git
cd Agenda-servicos
python -m venv .venv
```

Ativar o ambiente virtual:

```bash
.venv\Scripts\activate
```

(no Linux/Mac: `source .venv/bin/activate`)

Instalar as dependencias e criar o banco:

```bash
pip install -r requirements.txt
```

```bash
python manage.py migrate
```

Criar dados de exemplo (opcional, ajuda a gravar o video):

```bash
python manage.py popular_dados
```

Subir o servidor:

```bash
python manage.py runserver
```

Abrir <http://127.0.0.1:8000/>.

Para entrar no `/admin/`, crie um usuario administrador:

```bash
python manage.py createsuperuser
```

## Rodar os testes

```bash
python manage.py test
```

Os testes cobrem cadastro, busca, edicao e exclusao de clientes e servicos, o
comando `popular_dados` e, principalmente, a **regra de conflito de horario** dos
agendamentos. O resultado esperado termina em `OK`.

## Estrutura de pastas

```
Agenda-servicos/
├── config/              # configuracao do projeto Django (settings, urls raiz)
├── agenda/              # o app com a regra de negocio
│   ├── models.py        # CAMADA DE DADOS: Cliente, Servico e Agendamento
│   ├── forms.py         # validacao e montagem dos formularios
│   ├── views.py         # CAMADA DE BACK-END: o que acontece em cada URL
│   ├── urls.py          # quais enderecos existem
│   ├── admin.py         # configuracao do painel /admin
│   ├── tests.py         # testes automatizados
│   ├── migrations/      # historico das mudancas no banco
│   └── management/commands/popular_dados.py
├── templates/           # CAMADA DE FRONT-END: o HTML (base.html, agenda/, admin/)
├── static/css/          # estilo proprio (estilo.css do site, admin-salon.css do /admin)
├── requirements.txt     # dependencias
└── docs/                # documentacao (veja abaixo)
```

## Documentacao

| Documento | Para que serve |
|---|---|
| [`docs/COMECE-AQUI.md`](docs/COMECE-AQUI.md) | Indice e ordem de leitura, com checklist |
| [`docs/ENTENDENDO-O-CODIGO.md`](docs/ENTENDENDO-O-CODIGO.md) | Guia de estudo: fluxo de uma requisicao, arquivo por arquivo, glossario e perguntas do professor |
| [`docs/ARQUITETURA.md`](docs/ARQUITETURA.md) | Consulta: como o site funciona e como foi estruturado (pastas, enderecos, dados, telas, configuracoes, como acrescentar funcionalidades) |
| [`docs/CADASTROS.md`](docs/CADASTROS.md) | A primeira funcionalidade: cadastro, busca, edicao e exclusao de clientes e servicos, validacoes e limites |
| [`docs/AGENDAMENTO.md`](docs/AGENDAMENTO.md) | A funcionalidade de agendamento: telas, modelo de dados, regra de conflito, decisoes tecnicas e limites |
| [`docs/RELATORIOS.md`](docs/RELATORIOS.md) | A terceira funcionalidade: relatorios e faturamento por periodo, regras, onde esta cada coisa e limites |
| [`docs/EXPLICANDO-A-IMPLEMENTACAO.md`](docs/EXPLICANDO-A-IMPLEMENTACAO.md) | Como explicar o que foi implementado: roteiro, demonstracao e perguntas provaveis |
| [`docs/INFORMACOES-VIDEO.md`](docs/INFORMACOES-VIDEO.md) | O que mostrar e citar no video (nao e roteiro), como gravar e publicar |
| [`docs/ENTREGA.md`](docs/ENTREGA.md) | Branch, commits, tag, board e checklist final de entrega |

## Decisoes tecnicas

**SQLite no desenvolvimento.** Quem clonar o repositorio consegue rodar sem
instalar nenhum banco. A troca para PostgreSQL esta prevista para uma entrega
posterior e mexe em uma unica parte do `config/settings.py`.

**Views em funcao (nao em classe).** Django tem as *class-based views*, que
escrevem um CRUD com menos linhas. Aqui foram usadas funcoes de proposito:
da para ler cada view de cima a baixo e entender exatamente o que acontece,
o que importa mais do que economizar linhas em um projeto de aprendizado.

**`duracao_minutos` no `Servico` desde a primeira entrega.** Ela e usada pelo
`Agendamento` para calcular o fim do horario e detectar conflitos. Ter o campo
desde o inicio evitou mexer na tabela de servicos.

**Regra de conflito no model, nao na view.** A validacao fica em
`Agendamento.clean()`, entao vale tanto no site quanto no `/admin/`.
Detalhes em [`docs/AGENDAMENTO.md`](docs/AGENDAMENTO.md).

**Exclusao so acontece via POST.** A tela de confirmacao existe porque um
link `GET` que apaga dados pode ser disparado sem intencao do usuario.

**Cliente e servico com agendamento nao podem ser excluidos** (`on_delete=PROTECT`),
para nao perder o historico. Para tirar um servico de uso, basta desativa-lo.

**Avisos de erro em vermelho.** O Bootstrap so conhece `alert-danger`, e o Django
chama essa mensagem de `error`; o `MESSAGE_TAGS` do `settings.py` faz a traducao.

## Limitacoes e proximos passos

- **Sem login**: qualquer pessoa com o endereco consegue alterar os dados.
  Proximo passo natural: autenticacao e `login_required` nas views.
- **Um unico profissional**: um horario ocupado vale para toda a agenda. Para
  varios profissionais, o agendamento ganharia um campo `profissional`.
- **Sem paginacao** nas listas.
- **Banco SQLite**: a troca para PostgreSQL esta prevista.
- **Configuracao de desenvolvimento**: `SECRET_KEY` e `DEBUG=True` estao no
  `settings.py` apenas para desenvolvimento; antes de publicar o sistema de
  verdade, devem ir para variaveis de ambiente.
