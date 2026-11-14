# Funcionalidade: Historico do cliente

Esta e a quarta funcionalidade do projeto. Como os relatorios, ela **nao cria dados
novos**: le os agendamentos que ja existem e mostra a vida de um cliente no
sistema: *quanto ele ja gastou? quando veio pela ultima vez? quando volta?*

> **So agendamentos concluidos contam como gasto** (mesma regra do faturamento).

## 1. Visao rapida

| Pergunta | Resposta |
|---|---|
| Onde fica? | Lista de **Clientes**, botao **Historico** (`/clientes/<id>/historico/`) |
| Precisa de migration? | Nao: nenhum model foi alterado |
| Cliente inexistente? | Mostra a pagina 404 |

## 2. O que a tela mostra

| Item | Como e calculado |
|---|---|
| Total gasto | Soma do preco do servico dos agendamentos **concluidos** |
| Atendimentos concluidos | Contagem dos agendamentos concluidos |
| Ultimo atendimento | Data do concluido mais recente |
| Proximo horario | Agendamento **agendado** futuro mais proximo |
| Tabela | Todos os agendamentos do cliente, do mais novo para o mais antigo |

## 3. Onde esta no codigo

| Camada | Arquivo |
|---|---|
| Rota | `agenda/urls.py` (`cliente_historico`) |
| View | `agenda/views.py` (`cliente_historico`) |
| Template | `templates/agenda/cliente_historico.html` |
| Testes | `agenda/tests.py` (`HistoricoClienteTests`) |
