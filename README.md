# Agenda de Servicos

Sistema web de agendamento de servicos (barbearia / salao / clinica), feito em
**Python + Django** para a materia de Projeto de Software.

Funcionalidades:

- **Clientes** e **servicos**: cadastro, busca, edicao e exclusao.
- **Agendamentos**: marcar horario para um cliente e um servico, com filtro por
  data e situacao. O sistema **bloqueia horarios em conflito**, calculando o fim
  de cada agendamento pela duracao do servico. Explicacao completa em
  [`docs/AGENDAMENTO.md`](docs/AGENDAMENTO.md).
- **Painel inicial** com contadores e os proximos horarios.

Atende o requisito de **3 camadas**:

| Camada | Onde fica |
|---|---|
| Front-end | `templates/` + `static/css/` (HTML dos templates Django + Bootstrap 5) |
| Back-end | `agenda/views.py`, `agenda/forms.py`, `agenda/urls.py` |
| Banco de dados | `agenda/models.py` + migrations (SQLite no desenvolvimento) |

## Como rodar

Precisa de **Python 3.12 ou mais novo** instalado.

```bash
git clone <url-do-repositorio>
cd agenda-servicos
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

## Estrutura de pastas

```
agenda-servicos/
├── config/              # configuracao do projeto Django (settings, urls raiz)
├── agenda/              # o app com a regra de negocio
│   ├── models.py        # CAMADA DE DADOS: Cliente, Servico e Agendamento
│   ├── forms.py         # validacao e montagem dos formularios
│   ├── views.py         # CAMADA DE BACK-END: o que acontece em cada URL
│   ├── urls.py          # quais enderecos existem
│   ├── admin.py         # configuracao do painel /admin
│   ├── tests.py         # testes automatizados
│   └── management/commands/popular_dados.py
├── templates/           # CAMADA DE FRONT-END: o HTML
├── static/css/          # estilo proprio
├── requirements.txt     # dependencias
└── docs/                # documentacao (AGENDAMENTO.md)
```

## Documentacao

Comece por [`docs/COMECE-AQUI.md`](docs/COMECE-AQUI.md): ele diz a ordem de leitura.

| Documento | Para que serve |
|---|---|
| [`docs/COMECE-AQUI.md`](docs/COMECE-AQUI.md) | Indice, ordem de leitura e checklist |
| [`docs/ARQUITETURA.md`](docs/ARQUITETURA.md) | Consulta: pastas, enderecos, dados, telas e configuracoes |
| [`docs/CADASTROS.md`](docs/CADASTROS.md) | Cadastro de clientes e servicos |
| [`docs/AGENDAMENTO.md`](docs/AGENDAMENTO.md) | Agendamento: regras, conflito de horario, fluxo, testes e limitacoes |
| [`docs/EXPLICANDO-A-IMPLEMENTACAO.md`](docs/EXPLICANDO-A-IMPLEMENTACAO.md) | Como explicar o que foi implementado (roteiro, demonstracao, perguntas) |
| [`docs/ENTENDENDO-O-CODIGO.md`](docs/ENTENDENDO-O-CODIGO.md) | Guia de estudo do codigo |
| [`docs/INFORMACOES-VIDEO.md`](docs/INFORMACOES-VIDEO.md) | O que mostrar e citar no video |
| [`docs/ENTREGA.md`](docs/ENTREGA.md) | Repositorio, board e checklist de entrega |

## Decisoes tecnicas

**SQLite no desenvolvimento.** Quem clonar o repositorio consegue rodar sem
instalar nenhum banco. A troca para PostgreSQL esta prevista para uma entrega
posterior e mexe em uma unica parte do `config/settings.py`.

**Views em funcao (nao em classe).** Django tem as *class-based views*, que
escrevem um CRUD com menos linhas. Aqui foram usadas funcoes de proposito:
da para ler cada view de cima a baixo e entender exatamente o que acontece,
o que importa mais do que economizar linhas em um projeto de aprendizado.

**`duracao_minutos` no `Servico` desde a primeira entrega.** O `Agendamento`
usa a duracao para calcular o fim do horario e detectar conflitos. Ter o campo
desde o inicio evitou uma migration extra.

**Regra de conflito no model, nao na view.** A validacao fica em
`Agendamento.clean()`, entao vale tanto no site quanto no `/admin/`.

**Cliente e servico com agendamento nao podem ser excluidos**
(`on_delete=PROTECT`), para nao perder o historico. Para tirar um servico de
uso, basta desativa-lo.

**Exclusao so acontece via POST.** A tela de confirmacao existe porque um
link `GET` que apaga dados pode ser disparado sem intencao do usuario.

## Proximos passos

Depois de rodar o projeto, leia [`docs/COMECE-AQUI.md`](docs/COMECE-AQUI.md) e, para o agendamento, [`docs/AGENDAMENTO.md`](docs/AGENDAMENTO.md): ele
explica a funcionalidade de agendamento, as regras de negocio, como o conflito
de horario e detectado, onde fica cada arquivo, os testes e as limitacoes
conhecidas.

Para **explicar** o que foi implementado a outra pessoa (ordem sugerida,
demonstracao e perguntas provaveis), use
[`docs/EXPLICANDO-A-IMPLEMENTACAO.md`](docs/EXPLICANDO-A-IMPLEMENTACAO.md).
