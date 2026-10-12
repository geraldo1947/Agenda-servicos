# Funcionalidade: Cadastros de clientes e servicos

Primeira funcionalidade do projeto (entregue no AC1, presente desde o commit
inicial). Ela guarda **quem** marca horario (**Cliente**) e **o que** pode ser
marcado (**Servico**, com duracao e preco). E a base do
[Agendamento](AGENDAMENTO.md), que liga as duas coisas.

> Veja tambem: [ARQUITETURA.md](ARQUITETURA.md) (visao geral e configuracoes) e
> [ENTENDENDO-O-CODIGO.md](ENTENDENDO-O-CODIGO.md) (passo a passo de uma
> requisicao).

## O que o usuario consegue fazer

| Tela | Endereco | O que faz |
|---|---|---|
| Lista de clientes | `/clientes/` | Lista por ordem alfabetica; busca `?q=` por nome ou telefone |
| Novo cliente | `/clientes/novo/` | Cadastra |
| Editar cliente | `/clientes/<id>/editar/` | Altera os dados |
| Excluir cliente | `/clientes/<id>/excluir/` | Tela de confirmacao (GET); apaga so por POST |
| Lista de servicos | `/servicos/` | Lista por ordem alfabetica; busca `?q=` por nome |
| Novo servico | `/servicos/novo/` | Cadastra |
| Editar servico | `/servicos/<id>/editar/` | Altera os dados |
| Excluir servico | `/servicos/<id>/excluir/` | Tela de confirmacao (GET); apaga so por POST |

O painel inicial (`/`) mostra quantos clientes existem e quantos servicos estao
**ativos**. As mesmas tabelas estao no `/admin/`, com busca por nome.

## Os dados

| Tabela | Campo | Regra |
|---|---|---|
| **Cliente** | `nome` | obrigatorio, ate 120 caracteres |
| | `telefone` | obrigatorio, ate 20 caracteres (sem formato fixo) |
| | `email` | opcional; se preenchido, precisa ser um e-mail valido |
| | `criado_em` | automatico |
| **Servico** | `nome` | obrigatorio, ate 120 caracteres |
| | `descricao` | opcional |
| | `duracao_minutos` | inteiro, minimo 1, padrao 30; e a base do calculo do fim do agendamento |
| | `preco` | decimal com ate 8 digitos e 2 casas (ex.: `50.00`) |
| | `ativo` | caixa de marcar, ja marcada no cadastro novo |
| | `criado_em` | automatico |

As duas tabelas ficam em `agenda/models.py`; a migration que as cria e a
`agenda/migrations/0001_initial.py`.

## Como cada tela funciona

**Lista e busca.** A pagina le `?q=` da URL, tira os espacos das pontas e filtra
com "contem o texto": em clientes, o texto pode estar no **nome ou no telefone**;
em servicos, so no **nome**. O campo de busca volta preenchido com o que foi
digitado. Sem resultado, a tabela mostra "Nenhum ... encontrado".

**Cadastrar e editar.** Cliente e servico usam o **mesmo template** de formulario
(`templates/agenda/form.html`). Os campos vem do model (um `ModelForm`) e o
`BootstrapFormMixin` poe o estilo. Se algo estiver invalido, a mesma tela volta
com o erro embaixo do campo e com o que foi digitado preservado; se estiver certo,
salva, mostra a mensagem verde e volta para a lista.

**Excluir.** O botao leva a uma tela "Tem certeza?". So o botao dessa tela, que
envia um POST, apaga de verdade. Se o cliente ou o servico ja tiver agendamentos,
a exclusao e **bloqueada** e aparece um aviso vermelho (veja o `PROTECT` em
[AGENDAMENTO.md](AGENDAMENTO.md)). Para tirar um servico de uso sem apaga-lo,
desmarque **ativo**.

**Servico ativo e inativo.** Um servico inativo continua aparecendo na lista (com
o selo "inativo"), mas deixa de ser oferecido em novos agendamentos e de contar no
painel inicial.

## Decisoes tecnicas

- **Formularios gerados do model.** Escrever as regras uma vez, no model, e
  deixar o Django montar campo e validacao evita HTML repetido e regras
  duplicadas.
- **Views em funcao**, uma por acao (listar, novo, editar, excluir): cada uma se
  le de cima a baixo.
- **Exclusao so por POST**, com confirmacao: um link `GET` que apaga dados pode
  ser acionado sem querer (robo de busca, pre-carregamento do navegador).
- **`duracao_minutos` no servico desde o inicio**, porque o agendamento calcula o
  fim do horario com ela.
- **Mesmo template para criar e editar** e para clientes e servicos: menos arquivos,
  e o titulo e o botao Cancelar chegam pelo contexto (`titulo` e `voltar`).

## Limites conhecidos

- **A busca nao ignora acento e so equipara maiuscula e minuscula em letras sem
  acento.** E uma limitacao do SQLite: buscar `MARIA` acha "Maria", mas buscar uma
  palavra sem acento nao acha o nome cadastrado com acento, e uma letra acentuada
  digitada em maiuscula nao acha a mesma letra em minuscula.
- **Nada impede nome repetido**: dois clientes (ou dois servicos) com o mesmo nome
  sao aceitos. Para clientes isso e desejavel (homonimos); para servicos, pode
  confundir a escolha.
- **O formulario de servico aceita preco negativo.** A duracao tem minimo de 1
  minuto (a duracao 0 e recusada). Mudar a duracao de um servico atualiza o fim
  dos agendamentos futuros dele, e e recusado se algum passar a invadir outro.
- **Telefone sem formato**: qualquer texto de ate 20 caracteres vale.
- **A busca de servicos so olha o nome** (nao a descricao nem o preco).
- Sem paginacao: a lista mostra tudo.

## Onde cada coisa esta

| Camada | Arquivo |
|---|---|
| Dados | `agenda/models.py` (`Cliente`, `Servico`), `agenda/migrations/0001_initial.py` |
| Back-end | `agenda/forms.py` (`ClienteForm`, `ServicoForm`), `agenda/views.py` (`cliente_*`, `servico_*`), `agenda/urls.py` |
| Front-end | `templates/agenda/cliente_lista.html`, `servico_lista.html`, `form.html`, `confirmar_exclusao.html` |
| Admin | `agenda/admin.py` (`ClienteAdmin`, `ServicoAdmin`) |
| Dados de exemplo | `agenda/management/commands/popular_dados.py` |
| Testes | `agenda/tests.py` (`ClienteTests`, `ServicoTests`) |

## Testes

```bash
python manage.py test agenda.tests.ClienteTests agenda.tests.ServicoTests
```

Sao 9 testes. `ClienteTests` (6): cadastro, edicao, busca pelo nome, nome
obrigatorio, GET na exclusao nao apaga e POST apaga. `ServicoTests` (3): cadastro,
edicao e o texto de apresentacao com a duracao. A protecao de cliente e servico
com agendamento e testada em `AgendamentoTests`.

**O que os testes nao cobrem:** a busca por telefone e a busca de servicos, a
exclusao de um servico sem agendamentos, e a validacao de e-mail e dos campos do
servico. Foram conferidos a mao.

## Passos para demonstrar

1. `python manage.py popular_dados` e abrir **Clientes**.
2. Buscar parte de um nome e depois um telefone.
3. Cadastrar um cliente; tentar salvar em branco e mostrar os erros.
4. Editar o cliente e salvar.
5. Excluir: mostrar a tela de confirmacao antes de apagar.
6. Em **Servicos**, desmarcar **ativo** em um servico e mostrar o selo "inativo".
