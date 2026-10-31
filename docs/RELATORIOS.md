# Funcionalidade: Relatorios e faturamento

Esta e a terceira funcionalidade do projeto. Ela nao cria dados novos: **le o que
ja existe** (agendamentos, servicos e clientes) e responde perguntas do dia a dia:
*quanto faturei? quanto ainda vou receber? qual servico vende mais? quem mais vem aqui?*

> **So agendamentos concluidos contam como faturamento.**

## 1. Visao rapida

| Pergunta | Resposta |
|---|---|
| Onde fica? | Menu **Relatorios** (`/relatorios/`) |
| Qual o periodo padrao? | O mes atual |
| Como mudar o periodo? | Campos **De** e **Ate** e botao **Filtrar** (o dia final entra inteiro) |
| Precisa de migration? | Nao: nenhum model foi alterado |

## 2. O que a tela mostra

| Item | Como e calculado |
|---|---|
| Faturamento | Soma do preco do servico dos agendamentos **concluidos** |
| A receber | Soma do preco dos agendamentos ainda **agendados** |
| Taxa de cancelamento | cancelados / total, em % arredondada |
| Total, Concluidos, Agendados, Cancelados | Contagem por situacao |
| Servicos mais pedidos | Top 5 por quantidade, sem contar cancelados |
| Clientes mais frequentes | Top 5 por quantidade, sem contar cancelados |

O periodo considera a data de **inicio** do agendamento, no fuso `America/Sao_Paulo`.

## 3. Regras e casos especiais

- Data invalida na URL (`?inicio=abc`): aviso e volta para o mes atual, sem erro.
- Data final anterior a inicial: aviso e volta para o mes atual.
- Periodo sem agendamentos: valores `R$ 0,00` e a mensagem "Nenhum dado no periodo."
- Servicos e clientes sao agrupados pelo **id**, nao pelo nome, entao dois servicos
  com o mesmo nome continuam em linhas separadas.

## 4. O caminho de um pedido

1. `config/urls.py` entrega o endereco `/relatorios/` para `agenda/urls.py`.
2. `agenda/urls.py` aponta para a view `relatorios`.
3. `agenda/views.py` (`relatorios`) le o periodo, filtra os agendamentos e usa
   `aggregate`, `Count` e `Sum` do Django para o banco fazer as contas.
4. `templates/agenda/relatorios.html` desenha os cartoes e as duas tabelas.

## 5. Onde esta cada coisa

| O que | Onde |
|---|---|
| Logica e contas | `agenda/views.py`, funcao `relatorios` |
| Endereco | `agenda/urls.py` |
| Tela | `templates/agenda/relatorios.html` |
| Link no menu | `templates/base.html` |
| Testes | `agenda/tests.py`, classe `RelatorioTests` |

## 6. Decisoes tecnicas

**As contas ficam no banco, nao em Python.** `Sum` e `Count` com `filter=` fazem tudo
em uma consulta, em vez de percorrer os agendamentos um a um.

**Sem campo "pago".** O preco vem do cadastro do servico no momento da consulta.
Se o preco do servico mudar, o relatorio de meses antigos muda junto.

## 7. Testes

```bash
python manage.py test agenda.tests.RelatorioTests
```

Cobrem: faturamento so de concluidos, cancelados fora dos rankings, ordenacao,
filtro de periodo, dia final inteiro, datas invalidas e pagina sem dados.

## 8. Limitacoes conhecidas

- O preco nao e "congelado" no agendamento (ver decisoes tecnicas).
- Sem grafico e sem exportacao (CSV/PDF).
- Os rankings mostram so o Top 5.

## 9. Como estender

- Exportar o relatorio em CSV: nova view que reaproveita as mesmas consultas.
- Guardar `preco_cobrado` no `Agendamento` para congelar o valor historico.
- Grafico de faturamento por dia.
