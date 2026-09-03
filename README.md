# Agenda de Servicos

Sistema web de agendamento de servicos (barbearia / salao / clinica), feito em
**Python + Django** para a materia de Projeto de Software.

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
│   ├── models.py        # CAMADA DE DADOS: Cliente e Servico
│   ├── forms.py         # validacao e montagem dos formularios
│   ├── views.py         # CAMADA DE BACK-END: o que acontece em cada URL
│   ├── urls.py          # quais enderecos existem
│   ├── admin.py         # configuracao do painel /admin
│   ├── tests.py         # testes automatizados
│   └── management/commands/popular_dados.py
├── templates/           # CAMADA DE FRONT-END: o HTML
├── static/css/          # estilo proprio
├── requirements.txt     # dependencias
└── docs/                # planejamento das entregas e roteiro dos videos
```

## Decisoes tecnicas

**SQLite no desenvolvimento.** Quem clonar o repositorio consegue rodar sem
instalar nenhum banco. A troca para PostgreSQL esta prevista para uma entrega
posterior e mexe em uma unica parte do `config/settings.py`.

**Views em funcao (nao em classe).** Django tem as *class-based views*, que
escrevem um CRUD com menos linhas. Aqui foram usadas funcoes de proposito:
da para ler cada view de cima a baixo e entender exatamente o que acontece,
o que importa mais do que economizar linhas em um projeto de aprendizado.

**`duracao_minutos` no `Servico` desde a primeira entrega.** Ela nao e usada
ainda, mas a regra de conflito de horario da entrega seguinte depende dela
para calcular o fim de um agendamento. Colocar agora evita uma migration
extra depois.

**Exclusao so acontece via POST.** A tela de confirmacao existe porque um
link `GET` que apaga dados pode ser disparado sem intencao do usuario.

## Proximos passos

Depois de rodar o projeto, va para [`docs/COMECE-AQUI.md`](docs/COMECE-AQUI.md) —
e o indice que diz a ordem de ler o resto da documentacao (entender o
codigo, criar o repositorio, montar o board, gravar o video, entregar).
