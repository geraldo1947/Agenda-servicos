# Comece aqui

Este e o indice da documentacao. Siga na ordem: cada etapa leva a proxima.

| # | Etapa | Documento | Tempo estimado |
|---|---|---|---|
| 1 | Rodar o projeto | [README](../README.md) | 10 min |
| 2 | Entender o codigo | [ENTENDENDO-O-CODIGO.md](ENTENDENDO-O-CODIGO.md) | 2 a 3 h |
| 3 | Consultar a estrutura (pastas, enderecos, dados, configuracoes) | [ARQUITETURA.md](ARQUITETURA.md) | 30 min |
| 4 | Entender a primeira funcionalidade: cadastros de clientes e servicos | [CADASTROS.md](CADASTROS.md) | 20 min |
| 5 | Entender a segunda funcionalidade: agendamento | [AGENDAMENTO.md](AGENDAMENTO.md) | 30 min |
| 6 | Gravar o video | [INFORMACOES-VIDEO.md](INFORMACOES-VIDEO.md) | 1 h (com ensaio) |
| 7 | Repositorio, board e entrega | [ENTREGA.md](ENTREGA.md) | 1 h |

## O projeto em um paragrafo

Sistema web feito com **Django** para marcar horarios em uma barbearia, salao ou
clinica. Tem tres cadastros: **clientes**, **servicos** e **agendamentos**. A
regra de negocio principal e que *dois agendamentos nao podem ocupar o mesmo
horario*. O AC1 entregou os cadastros de clientes e servicos; o AC2 acrescentou os
agendamentos. O sistema segue tres camadas: front-end (templates), back-end (views e
forms) e banco de dados (models).

## Checklist de progresso

Marque conforme for avancando.

**1. Rodar**
- [ ] Criei o ambiente virtual e instalei as dependencias
- [ ] Rodei `python manage.py migrate` e `python manage.py popular_dados`
- [ ] Abri `http://127.0.0.1:8000/` e naveguei por todas as telas
- [ ] `python manage.py test` terminou com `OK`
- [ ] `python manage.py check` terminou sem erros e sem avisos

**2. Entender**
- [ ] Consigo explicar as 3 camadas e apontar o arquivo de cada uma
- [ ] Sei onde olhar para achar um endereco, um campo do banco ou uma configuracao ([ARQUITETURA.md](ARQUITETURA.md))
- [ ] Segui o caminho de "criar agendamento" do navegador ate o banco
- [ ] Consigo explicar o cadastro e a busca de clientes e servicos ([CADASTROS.md](CADASTROS.md))
- [ ] Sei explicar como o sistema detecta conflito de horario
- [ ] Respondi em voz alta as perguntas da secao "O professor pode perguntar"
- [ ] Fiz os exercicios "mexa e veja"

**3. Video**
- [ ] Decidi o que vou mostrar e ensaiei pelo menos uma vez com o cronometro (4 minutos)
- [ ] Gravei, assisti de volta e conferi o audio

**4. Entrega**
- [ ] Repositorio criado e com commits organizados
- [ ] Board montado
- [ ] Checklist final de [ENTREGA.md](ENTREGA.md) completo

## Dica de estudo

Nao tente ler tudo de uma vez. Rode o sistema, use cada tela e so depois abra o
codigo da tela que acabou de usar. Fica muito mais facil ligar o que se ve na
tela com o que esta escrito.

## Se algo der errado

| Problema | Solucao |
|---|---|
| `python` nao e reconhecido | Instale o Python 3.12 ou mais novo e marque "Add to PATH" |
| `No module named django` | O ambiente virtual nao esta ativo, ou faltou `pip install -r requirements.txt` |
| `no such table` | Faltou rodar `python manage.py migrate` |
| Pagina sem estilo | Falta de internet (o Bootstrap vem de um CDN) |
| Quero recomecar do zero | Apague o arquivo `db.sqlite3` e rode `migrate` e `popular_dados` de novo |
