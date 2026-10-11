# Entrega: repositorio, board e checklist final

Passo a passo para organizar o projeto antes de entregar. Confira no enunciado
da disciplina o que e exigido (link do repositorio, link do video, formato do
board etc.) e ajuste o que for diferente.

## 1. Conferir antes de tudo

```bash
python manage.py test
python manage.py check
```

Os dois precisam terminar sem erros.

## 2. Repositorio, commits e entrega no GitHub

O repositorio ja existe: <https://github.com/geraldo1947/Agenda-servicos>. A
branch `main` guarda o que ja foi entregue (hoje, o AC1: clientes e servicos). O
trabalho de cada entrega acontece em uma **branch propria** e so entra na `main`
quando estiver pronto. Assim a `main` e sempre uma versao que roda.

### 2.1 Conferir a branch de trabalho

```bash
git status
```

Deve mostrar a branch `ac2-agendamento`. O `.gitignore` do projeto ja impede que
`db.sqlite3`, `.venv/` e `__pycache__/` sejam enviados: esses nomes **nao** devem
aparecer na lista do `git status`.

### 2.2 Commits organizados
Prefira alguns commits pequenos, cada um com uma ideia, a um unico commit gigante.
Cada commit abaixo deixa o sistema funcionando. O historico deve contar o que
realmente aconteceu, na ordem real: quem corrige o trabalho costuma olhar o
historico, e ele precisa bater com a sua explicacao no video.

```bash
git add config/settings.py
git commit -m "Mapeia o aviso de erro para alert-danger do Bootstrap"

git add agenda/models.py agenda/migrations/0002_agendamento.py agenda/admin.py
git commit -m "Adiciona model Agendamento com regra de conflito de horario"

git add agenda/forms.py agenda/views.py agenda/urls.py templates/ agenda/management/commands/popular_dados.py
git commit -m "Adiciona telas de agendamento e protege cliente/servico com agendamento"

git add agenda/tests.py
git commit -m "Adiciona testes de agendamento e cobre lacunas de cliente e servico"

git add README.md docs/
git commit -m "Adiciona documentacao do projeto: cadastros, agendamento, arquitetura e guias de entrega"
```

Se algum `git add` reclamar de arquivo inexistente, confira o nome com `git status`.
Depois confira: `git log --oneline` mostra os commits e `git status` diz
`nothing to commit, working tree clean`.

> O **autor** de cada commit e a identidade configurada na maquina de quem
> commita (`git config user.name` e `git config user.email`). Confira antes do
> primeiro commit que e a que voce quer no historico.

### 2.3 Enviar

```bash
git push -u origin ac2-agendamento
```

Em seguida, junte na `main`: abra um **Pull Request** no GitHub e faca o *merge*
(ou, localmente, `git switch main`, `git merge ac2-agendamento` e `git push`).

### 2.4 Marcar a entrega com uma tag

O professor abre o link do GitHub **depois** da entrega, quando a `main` ja pode
ter avancado. A tag congela o codigo daquele dia:

```bash
git tag -a ac2 -m "Entrega AC2 - agendamento com bloqueio de horario"
git push origin ac2
```

O link que vai para a entrega e `https://github.com/geraldo1947/Agenda-servicos/tree/ac2`.
Nas proximas entregas: `ac3` e `final`.

### 2.5 Teste de quem clona
Para ter certeza de que funciona em outra maquina, clone em uma pasta nova e siga
o README do zero:

```bash
git clone https://github.com/geraldo1947/Agenda-servicos.git teste-clone
cd teste-clone
python -m venv .venv
```

Ative o ambiente (Windows: `.venv\Scripts\activate`; Linux/Mac:
`source .venv/bin/activate`) e rode `pip install -r requirements.txt`,
`python manage.py migrate` e `python manage.py test`. Se o README levou ate
aqui sem voce improvisar nada, esta bom.

## 3. Montar o board

Um board (Kanban) mostra o planejamento e o andamento. Pode ser o **GitHub
Projects** (criado no seu perfil e ligado ao repositorio) ou o Trello. O passo a
passo abaixo e para o GitHub Projects.

### Passo a passo (GitHub Projects)

O repositorio precisa existir no GitHub antes (secao 2).

1. Clique na sua foto (canto superior direito do GitHub), em **Your profile**,
   abra a aba **Projects** e clique em **New project**.
2. Em "Start from scratch", escolha **Board**. Nomeie como `Agenda de Servicos`
   e clique em **Create project**. O quadro ja vem com tres colunas (`Todo`,
   `In Progress` e `Done`), que correspondem a `A fazer`, `Fazendo` e `Feito`.
3. **Cartoes:** no rodape de cada coluna, clique em **+ Add item**, digite o
   texto e aperte Enter. Nao precisa criar *issues*: um cartao de texto serve.
   Use a tabela de cartoes abaixo.
4. **Mover:** arraste o cartao para a coluna certa. O que ja foi concluido vai
   para `Done`.
5. **Ligar ao repositorio:** abra a pagina do repositorio no GitHub, clique na
   aba **Projects**, em **Link a project** e escolha o board.
6. **Deixar publico:** abra o board, clique no menu `...` (canto superior
   direito), em **Settings**, e em "Danger zone" escolha **Public** ao lado de
   **Visibility**. O board nasce privado; sem isso o professor ve uma pagina de
   erro.
7. **Pegar o link:** copie o endereco da barra do navegador (algo como
   `https://github.com/users/geraldo1947/projects/1`). O link e o mesmo em todas
   as entregas; o que muda e quais cartoes estao em `Done`.
8. Abra o link numa **aba anonima** para confirmar que funciona sem login.

### Colunas
`A fazer` | `Fazendo` | `Feito`

### Cartoes sugeridos
Baseados nas etapas reais do projeto. Mova para `Feito` o que ja foi concluido.

| Cartao | Entrega |
|---|---|
| Criar projeto Django e configurar banco | AC1 |
| Model Cliente + CRUD | AC1 |
| Model Servico + CRUD | AC1 |
| Busca nas listas | AC1 |
| Exclusao com confirmacao (so POST) | AC1 |
| Comando `popular_dados` | AC1 |
| Model Agendamento (cliente, servico, inicio, fim, status) | AC2 |
| Regra de conflito de horario | AC2 |
| CRUD de agendamentos com filtro por data e situacao | AC2 |
| Proteger cliente/servico que tem agendamento | AC2 |
| Testes automatizados | AC1/AC2 |
| Documentacao do projeto | AC2 |
| Gravar e enviar o video | AC2 |
| Login de usuarios | Futuro |
| Paginacao das listas | Futuro |
| Migrar para PostgreSQL | Futuro |

Dica: no GitHub Projects, voce pode anexar cada cartao ao *issue* ou ao commit
correspondente, o que deixa o board mais convincente.

## 4. Checklist final

**Codigo**
- [ ] `python manage.py test` termina com `OK`
- [ ] `python manage.py check` sem erros e sem avisos
- [ ] O sistema roda do zero seguindo o README

**Repositorio**
- [ ] Commits com mensagens claras, feitos na branch da entrega e juntados na `main`
- [ ] Tag da entrega criada (`ac2`) e o link `.../tree/ac2` abre o codigo certo
- [ ] Sem `db.sqlite3`, `.venv/` ou `__pycache__/` no repositorio
- [ ] Pasta `docs/` e README aparecem corretamente no GitHub
- [ ] Repositorio acessivel para o professor (publico, ou privado com convite)

**Video**
- [ ] Dentro do tempo combinado (4 minutos) e do limite do enunciado
- [ ] Audio claro, tela legivel
- [ ] Mostra o sistema funcionando e explica o codigo
- [ ] Link funcionando (teste abrindo em aba anonima)

**Board**
- [ ] Colunas e cartoes criados
- [ ] Link acessivel para o professor (board **publico**, ligado ao repositorio, testado em aba anonima)

**Entrega**
- [ ] Links do repositorio, do video e do board colados onde a disciplina pede
- [ ] Entregue antes do prazo, com folga

## 5. Se o professor perguntar...

Veja [ENTENDENDO-O-CODIGO.md](ENTENDENDO-O-CODIGO.md), secao
"O professor pode perguntar". Estude ate conseguir responder sem olhar.
