# Informacoes para o video

O video e responsabilidade de quem apresenta: o que falar, a ordem e o ritmo
ficam por sua conta. Este documento **nao e um roteiro**. Ele reune o que o
sistema faz e o que voce pode citar, para voce montar o video do seu jeito.

**Duracao combinada: 4 minutos.** Confira no enunciado da disciplina se o limite
oficial e outro. Em 4 minutos nao cabe tudo: escolha o que quer destacar.

## Antes de gravar

```bash
python manage.py migrate
python manage.py popular_dados
python manage.py test
python manage.py runserver
```

- [ ] Banco limpo e com dados de exemplo (apague `db.sqlite3` e refaca os comandos se precisar)
- [ ] Testes passando (`OK`), caso queira mostrar isso no video
- [ ] Navegador em tela cheia, com zoom em 110% ou 125% para a letra ficar legivel
- [ ] Se for mostrar codigo, o editor ja aberto nos arquivos que pretende mostrar
- [ ] Notificacoes do computador desligadas
- [ ] Microfone testado (grave 10 segundos e escute)

**Dados que o `popular_dados` cria** (o comando so cria agendamentos se ainda
nao existir nenhum, entao rodar de novo nao duplica)

| Cliente | Servico | Quando |
|---|---|---|
| Maria Silva | Corte de cabelo (30 min) | amanha, 09:00 as 09:30 |
| Joao Souza | Coloracao (90 min) | amanha, 10:00 as 11:30 |
| Ana Pereira | Manicure (45 min) | depois de amanha, 14:30 as 15:15 |

## O que o sistema faz (para demonstrar)

- **Clientes e servicos:** cadastro, busca, edicao e exclusao, com tela de confirmacao.
- **Agendamentos:** lista com filtro por data e por situacao; marcar, editar e
  excluir horarios. Informa-se so o inicio: o sistema calcula o fim somando a
  duracao do servico (um corte de 30 minutos as 14:00 aparece como `14:00 - 14:30`).
- **Conflito de horario:** ao marcar um horario que se sobrepoe a outro, o
  sistema recusa e diz qual horario esta ocupado. Um horario que so encosta no
  outro (um termina 14:30, o outro comeca 14:30) e aceito.
- **Cancelado libera o horario:** mudar a situacao para *Cancelado* deixa o horario livre.
- **Protecao do historico:** cliente ou servico que ja tem agendamento nao pode
  ser excluido (a tela avisa; para servicos, sugere desativar).
- **Painel inicial:** contadores e os 5 proximos horarios.
- **Painel `/admin/`:** tambem aplica a regra de conflito.

Para reproduzir o conflito com os dados de exemplo: crie um agendamento
amanha as 14:00 (Corte de cabelo) e tente outro as 14:15. O de 14:30 e aceito.

## Pontos tecnicos que podem ser citados

Use os que fizerem sentido para o que voce quer explicar:

- O projeto tem as **3 camadas** da disciplina: front-end em `templates/`,
  back-end em `agenda/views.py`, `forms.py` e `urls.py`, e dados em
  `agenda/models.py` com as migrations (SQLite).
- O **fim e calculado no `save()`** (inicio + duracao do servico) e guardado no
  banco, para a busca de conflitos ser uma consulta simples.
- Dois horarios se **sobrepoem** quando cada um comeca antes do outro terminar
  (`inicio__lt` e `fim__gt`, estritos, por isso "encostar" nao conta).
- A regra mora no **model** (`Agendamento.clean()`), nao na view; por isso vale
  tambem no `/admin/`.
- As chaves estrangeiras usam **`on_delete=PROTECT`**.
- O formulario nao deixa marcar no passado, mas deixa editar um agendamento
  antigo (para marcar como concluido) e mostra so servicos ativos.
- A exclusao so acontece por **POST**, com tela de confirmacao.
- Depois de um POST bem-sucedido a view faz **redirect** (evita reenviar o
  formulario ao apertar F5).
- Existem **44 testes automatizados**, incluindo os casos de conflito.
- **Limitacoes** (vale ser honesto sobre elas): ainda nao ha login; so existe um
  profissional (um horario ocupado vale para toda a agenda); a lista nao tem
  paginacao (veja `AGENDAMENTO.md`).

## Onde cada coisa esta no codigo

| Assunto | Onde |
|---|---|
| Calculo do fim, regra de conflito, `PROTECT` | `agenda/models.py` (`Agendamento`) |
| Validacao de passado, servicos ativos | `agenda/forms.py` (`AgendamentoForm`) |
| Telas e protecao ao excluir | `agenda/views.py` |
| Mensagem de conflito na tela | `templates/agenda/form.html` |
| Lista e filtros | `templates/agenda/agendamento_lista.html` |
| Testes da regra | `agenda/tests.py` (`AgendamentoTests`) |
| Cadastros e busca de clientes e servicos | `agenda/views.py` (`cliente_*` e `servico_*`); detalhes em [CADASTROS.md](CADASTROS.md) |

Para entender cada um com calma, veja [ENTENDENDO-O-CODIGO.md](ENTENDENDO-O-CODIGO.md).

## Como gravar a tela (Windows)

Nao precisa instalar nada: o Windows ja tem um gravador.

1. Abra o navegador na tela do sistema (`127.0.0.1:8000`).
2. Aperte **Windows + G** para abrir a Xbox Game Bar.
3. Clique no botao redondo de gravar (ou **Windows + Alt + R**).
4. Aperte **Windows + Alt + R** de novo para parar.

O arquivo e salvo em `Videos > Capturas` na pasta do usuario.

## Como publicar o link do video

O que se entrega costuma ser um **link**, nao o arquivo.

- **Google Drive:** envie o `.mp4`, clique em *Compartilhar* e troque "Restrito"
  por **"Qualquer pessoa com o link"**. Sem isso, o professor ve "acesso negado".
- **YouTube:** envie em <https://studio.youtube.com> com visibilidade **Nao listado**.

Teste o link numa **aba anonima** antes de entregar.

## Se algo der errado na gravacao

| Problema | O que fazer |
|---|---|
| O sistema mostrou erro | Pare, apague `db.sqlite3`, rode `migrate` e `popular_dados` e recomece |
| Passou do tempo | Corte o que for secundario; o essencial e o sistema funcionando |
| O horario "amanha as 14:00" ja existe | Escolha outro horario livre; o que importa e mostrar o conflito |
| Errou uma fala | Pare, respire e repita a frase; corte depois |

## Checklist antes de enviar o video

- [ ] Dentro do tempo combinado (4 minutos) e do limite do enunciado
- [ ] Audio claro e tela legivel
- [ ] Mostra o sistema funcionando
- [ ] Link aberto em aba anonima, funcionando
