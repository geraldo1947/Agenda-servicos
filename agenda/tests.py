from datetime import timedelta
from io import StringIO

from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Agendamento, Cliente, Servico


class ClienteTests(TestCase):
    def test_cadastra_cliente_pelo_formulario(self):
        resposta = self.client.post(
            reverse("cliente_novo"),
            {"nome": "Maria Silva", "telefone": "11999998888", "email": "maria@exemplo.com"},
        )
        self.assertRedirects(resposta, reverse("cliente_lista"))
        self.assertEqual(Cliente.objects.count(), 1)

    def test_busca_filtra_pelo_nome(self):
        Cliente.objects.create(nome="Maria Silva", telefone="1111")
        Cliente.objects.create(nome="Joao Souza", telefone="2222")

        resposta = self.client.get(reverse("cliente_lista"), {"q": "maria"})

        self.assertContains(resposta, "Maria Silva")
        self.assertNotContains(resposta, "Joao Souza")

    def test_get_na_exclusao_nao_apaga_o_registro(self):
        cliente = Cliente.objects.create(nome="Maria Silva", telefone="1111")

        self.client.get(reverse("cliente_excluir", args=[cliente.pk]))

        self.assertEqual(Cliente.objects.count(), 1)

    def test_edita_cliente_pelo_formulario(self):
        cliente = Cliente.objects.create(nome="Maria Silva", telefone="1111")

        resposta = self.client.post(
            reverse("cliente_editar", args=[cliente.pk]),
            {"nome": "Maria Souza", "telefone": "1111", "email": ""},
        )

        self.assertRedirects(resposta, reverse("cliente_lista"))
        cliente.refresh_from_db()
        self.assertEqual(cliente.nome, "Maria Souza")

    def test_nome_e_obrigatorio(self):
        resposta = self.client.post(reverse("cliente_novo"), {"nome": "", "telefone": "1111", "email": ""})

        self.assertContains(resposta, "obrigat")
        self.assertEqual(Cliente.objects.count(), 0)

    def test_post_na_exclusao_apaga_o_cliente(self):
        cliente = Cliente.objects.create(nome="Maria Silva", telefone="1111")

        self.client.post(reverse("cliente_excluir", args=[cliente.pk]))

        self.assertEqual(Cliente.objects.count(), 0)


class ServicoTests(TestCase):
    def test_cadastra_servico_pelo_formulario(self):
        resposta = self.client.post(
            reverse("servico_novo"),
            {"nome": "Corte", "descricao": "", "duracao_minutos": 30, "preco": "50.00", "ativo": "on"},
        )
        self.assertRedirects(resposta, reverse("servico_lista"))
        self.assertEqual(Servico.objects.count(), 1)

    def test_str_do_servico_mostra_duracao(self):
        servico = Servico.objects.create(nome="Corte", duracao_minutos=45, preco=50)

        self.assertEqual(str(servico), "Corte (45 min)")

    def test_edita_servico_pelo_formulario(self):
        servico = Servico.objects.create(nome="Corte", duracao_minutos=30, preco=50)

        self.client.post(
            reverse("servico_editar", args=[servico.pk]),
            {"nome": "Corte", "descricao": "", "duracao_minutos": 45, "preco": "55.00", "ativo": "on"},
        )

        servico.refresh_from_db()
        self.assertEqual(servico.duracao_minutos, 45)


class HomeTests(TestCase):
    def test_home_mostra_os_proximos_agendamentos(self):
        cliente = Cliente.objects.create(nome="Maria Silva", telefone="1111")
        servico = Servico.objects.create(nome="Corte", duracao_minutos=30, preco=50)
        Agendamento.objects.create(
            cliente=cliente, servico=servico, inicio=timezone.now() + timedelta(days=1)
        )

        resposta = self.client.get(reverse("home"))

        self.assertEqual(resposta.context["total_agendamentos"], 1)
        self.assertContains(resposta, "Maria Silva")

    def test_home_nao_conta_agendamento_cancelado(self):
        cliente = Cliente.objects.create(nome="Maria Silva", telefone="1111")
        servico = Servico.objects.create(nome="Corte", duracao_minutos=30, preco=50)
        Agendamento.objects.create(
            cliente=cliente, servico=servico, inicio=timezone.now() + timedelta(days=1),
            status=Agendamento.Status.CANCELADO,
        )

        resposta = self.client.get(reverse("home"))

        self.assertEqual(resposta.context["total_agendamentos"], 0)


class PopularDadosTests(TestCase):
    def test_rodar_duas_vezes_nao_duplica_os_dados(self):
        call_command("popular_dados", stdout=StringIO())
        call_command("popular_dados", stdout=StringIO())

        self.assertEqual(Cliente.objects.count(), 3)
        self.assertEqual(Servico.objects.count(), 3)
        self.assertEqual(Agendamento.objects.count(), 3)


class AgendamentoTests(TestCase):
    def setUp(self):
        self.cliente = Cliente.objects.create(nome="Maria Silva", telefone="1111")
        self.outro_cliente = Cliente.objects.create(nome="Joao Souza", telefone="2222")
        self.corte = Servico.objects.create(nome="Corte", duracao_minutos=30, preco=50)
        # Amanha as 10:00, para nunca cair no passado.
        self.base = (timezone.localtime() + timedelta(days=1)).replace(hour=10, minute=0, second=0, microsecond=0)

    def criar(self, inicio, cliente=None, servico=None, **extra):
        return Agendamento.objects.create(
            cliente=cliente or self.cliente, servico=servico or self.corte, inicio=inicio, **extra
        )

    def dados_form(self, inicio, **extra):
        dados = {
            "cliente": self.outro_cliente.pk,
            "servico": self.corte.pk,
            "inicio": inicio.strftime("%Y-%m-%dT%H:%M"),
            "status": "agendado",
            "observacoes": "",
        }
        dados.update(extra)
        return dados

    # --- calculo do fim ---

    def test_fim_e_inicio_mais_duracao_do_servico(self):
        ag = self.criar(self.base)

        self.assertEqual(ag.fim, self.base + timedelta(minutes=30))

    # --- regra de conflito (model) ---

    def test_horario_sobreposto_e_recusado(self):
        self.criar(self.base)
        novo = Agendamento(cliente=self.outro_cliente, servico=self.corte, inicio=self.base + timedelta(minutes=15))

        with self.assertRaises(ValidationError):
            novo.full_clean()

    def test_mesmo_horario_e_recusado(self):
        self.criar(self.base)
        novo = Agendamento(cliente=self.outro_cliente, servico=self.corte, inicio=self.base)

        with self.assertRaises(ValidationError):
            novo.full_clean()

    def test_horario_que_engloba_outro_e_recusado(self):
        # Maria ocupa 10:00-10:30; uma coloracao de 90 min comecando 09:30 cobre esse intervalo todo.
        coloracao = Servico.objects.create(nome="Coloracao", duracao_minutos=90, preco=180)
        self.criar(self.base)
        novo = Agendamento(
            cliente=self.outro_cliente, servico=coloracao, inicio=self.base - timedelta(minutes=30)
        )

        with self.assertRaises(ValidationError):
            novo.full_clean()

    def test_horario_colado_no_fim_do_outro_e_aceito(self):
        self.criar(self.base)  # 10:00-10:30
        novo = Agendamento(cliente=self.outro_cliente, servico=self.corte, inicio=self.base + timedelta(minutes=30))

        novo.full_clean()  # nao deve levantar erro

    def test_horario_colado_no_inicio_do_outro_e_aceito(self):
        self.criar(self.base)  # 10:00-10:30
        novo = Agendamento(cliente=self.outro_cliente, servico=self.corte, inicio=self.base - timedelta(minutes=30))

        novo.full_clean()  # termina exatamente quando o outro comeca

    def test_agendamento_cancelado_libera_o_horario(self):
        self.criar(self.base, status=Agendamento.Status.CANCELADO)
        novo = Agendamento(cliente=self.outro_cliente, servico=self.corte, inicio=self.base)

        novo.full_clean()

    def test_reativar_agendamento_cancelado_volta_a_checar_conflito(self):
        cancelado = self.criar(self.base, status=Agendamento.Status.CANCELADO)
        self.criar(self.base, cliente=self.outro_cliente)  # outro ocupa o mesmo horario
        cancelado.status = Agendamento.Status.AGENDADO

        with self.assertRaises(ValidationError):
            cancelado.full_clean()

    def test_editar_sem_mudar_horario_nao_conflita_consigo_mesmo(self):
        ag = self.criar(self.base)
        ag.observacoes = "trazer foto de referencia"

        ag.full_clean()

    # --- telas ---

    def test_cadastra_agendamento_pelo_formulario(self):
        resposta = self.client.post(reverse("agendamento_novo"), self.dados_form(self.base))

        self.assertRedirects(resposta, reverse("agendamento_lista"))
        self.assertEqual(Agendamento.objects.count(), 1)

    def test_formulario_mostra_erro_de_conflito_e_nao_salva(self):
        self.criar(self.base)

        resposta = self.client.post(reverse("agendamento_novo"), self.dados_form(self.base))

        self.assertContains(resposta, "Horario indisponivel")
        self.assertEqual(Agendamento.objects.count(), 1)

    def test_editar_para_dentro_de_outro_horario_e_recusado(self):
        self.criar(self.base)
        livre = self.criar(self.base + timedelta(hours=3), cliente=self.outro_cliente)

        resposta = self.client.post(
            reverse("agendamento_editar", args=[livre.pk]), self.dados_form(self.base + timedelta(minutes=15))
        )

        self.assertContains(resposta, "Horario indisponivel")
        livre.refresh_from_db()
        self.assertEqual(livre.inicio, self.base + timedelta(hours=3))

    def test_formulario_recusa_data_no_passado(self):
        passado = self.base - timedelta(days=10)

        resposta = self.client.post(reverse("agendamento_novo"), self.dados_form(passado))

        self.assertContains(resposta, "no futuro")
        self.assertEqual(Agendamento.objects.count(), 0)

    def test_servico_inativo_nao_aparece_no_formulario_novo(self):
        Servico.objects.create(nome="Servico antigo", duracao_minutos=20, preco=10, ativo=False)

        resposta = self.client.get(reverse("agendamento_novo"))

        self.assertNotContains(resposta, "Servico antigo")

    def test_lista_filtra_por_data(self):
        self.criar(self.base)
        self.criar(self.base + timedelta(days=3), cliente=self.outro_cliente)

        resposta = self.client.get(reverse("agendamento_lista"), {"data": self.base.strftime("%Y-%m-%d")})

        self.assertContains(resposta, "Maria Silva")
        self.assertNotContains(resposta, "Joao Souza")

    def test_lista_filtra_por_situacao(self):
        self.criar(self.base)
        self.criar(self.base + timedelta(days=1), cliente=self.outro_cliente, status=Agendamento.Status.CANCELADO)

        resposta = self.client.get(reverse("agendamento_lista"), {"status": "cancelado"})

        self.assertContains(resposta, "Joao Souza")
        self.assertNotContains(resposta, "Maria Silva")

    def test_lista_ignora_filtros_invalidos(self):
        self.criar(self.base)

        for filtros in ({"data": "lixo"}, {"data": "2026-13-45"}, {"status": "inventado"}):
            resposta = self.client.get(reverse("agendamento_lista"), filtros)

            self.assertEqual(resposta.status_code, 200)
            self.assertContains(resposta, "Maria Silva")

    def test_get_na_exclusao_nao_apaga_o_agendamento(self):
        ag = self.criar(self.base)

        self.client.get(reverse("agendamento_excluir", args=[ag.pk]))

        self.assertEqual(Agendamento.objects.count(), 1)

    def test_post_na_exclusao_apaga_o_agendamento(self):
        ag = self.criar(self.base)

        self.client.post(reverse("agendamento_excluir", args=[ag.pk]))

        self.assertEqual(Agendamento.objects.count(), 0)

    # --- protecao do historico ---

    def test_cliente_com_agendamento_nao_pode_ser_excluido(self):
        self.criar(self.base)

        resposta = self.client.post(reverse("cliente_excluir", args=[self.cliente.pk]), follow=True)

        self.assertTrue(Cliente.objects.filter(pk=self.cliente.pk).exists())
        # O aviso precisa aparecer em vermelho (alert-danger), nao so existir.
        self.assertContains(resposta, "o cliente possui agendamentos")
        self.assertContains(resposta, 'class="alert alert-danger')

    def test_servico_com_agendamento_nao_pode_ser_excluido(self):
        self.criar(self.base)

        resposta = self.client.post(reverse("servico_excluir", args=[self.corte.pk]), follow=True)

        self.assertTrue(Servico.objects.filter(pk=self.corte.pk).exists())
        self.assertContains(resposta, "o servico possui agendamentos")
        self.assertContains(resposta, 'class="alert alert-danger')

    def test_agendamento_antigo_pode_ser_marcado_como_concluido(self):
        # Cria direto no banco (sem passar pelo form) um horario que ja passou.
        passado = self.base - timedelta(days=10)
        ag = self.criar(passado)

        resposta = self.client.post(
            reverse("agendamento_editar", args=[ag.pk]),
            self.dados_form(passado, cliente=self.cliente.pk, status="concluido"),
        )

        self.assertRedirects(resposta, reverse("agendamento_lista"))
        ag.refresh_from_db()
        self.assertEqual(ag.status, Agendamento.Status.CONCLUIDO)

    def test_cancelar_do_formulario_volta_para_a_lista(self):
        # Data no passado faz o formulario ser exibido de novo, com o botao Cancelar.
        # O teste confere o proprio link: so procurar o endereco nao serve, porque
        # o menu de toda pagina ja tem /agendamentos/ e o teste passaria sempre.
        resposta = self.client.post(reverse("agendamento_novo"), self.dados_form(self.base - timedelta(days=10)))

        self.assertContains(
            resposta,
            f'<a href="{reverse("agendamento_lista")}" class="btn btn-link">Cancelar</a>',
            html=True,
        )

    def test_trocar_para_servico_mais_longo_que_invade_o_proximo_e_recusado(self):
        # 10:00-10:30 (Corte) e outro as 11:00. Trocar o primeiro para um
        # servico de 90 min iria ate 11:30 e invadiria o das 11:00.
        longo = Servico.objects.create(nome="Coloracao", duracao_minutos=90, preco=180)
        primeiro = self.criar(self.base)
        self.criar(self.base + timedelta(minutes=60), cliente=self.outro_cliente)

        resposta = self.client.post(
            reverse("agendamento_editar", args=[primeiro.pk]),
            self.dados_form(self.base, cliente=self.cliente.pk, servico=longo.pk),
        )

        self.assertContains(resposta, "Horario indisponivel")
        primeiro.refresh_from_db()
        self.assertEqual(primeiro.servico, self.corte)


    # --- duracao minima do servico ---

    def test_servico_com_duracao_zero_e_recusado(self):
        resposta = self.client.post(
            reverse("servico_novo"),
            {"nome": "Instantaneo", "descricao": "", "duracao_minutos": 0, "preco": "10.00", "ativo": "on"},
        )

        self.assertEqual(resposta.status_code, 200)
        self.assertFalse(Servico.objects.filter(nome="Instantaneo").exists())

    # --- mudanca de duracao do servico ---

    def editar_duracao(self, servico, minutos):
        return self.client.post(
            reverse("servico_editar", args=[servico.pk]),
            {"nome": servico.nome, "descricao": "", "duracao_minutos": minutos, "preco": "50.00", "ativo": "on"},
        )

    def test_mudar_duracao_recalcula_o_fim_dos_agendamentos_futuros(self):
        ag = self.criar(self.base)

        resposta = self.editar_duracao(self.corte, 60)

        self.assertRedirects(resposta, reverse("servico_lista"))
        ag.refresh_from_db()
        self.assertEqual(ag.fim, self.base + timedelta(minutes=60))

    def test_mudar_duracao_nao_mexe_em_agendamento_passado(self):
        passado = self.base - timedelta(days=10)
        ag = self.criar(passado)

        self.editar_duracao(self.corte, 60)

        ag.refresh_from_db()
        self.assertEqual(ag.fim, passado + timedelta(minutes=30))

    def test_mudar_duracao_que_invade_outro_horario_e_recusado(self):
        # 10:00-10:30 (Corte) e outro as 10:45. Passar o Corte para 60 min
        # faria o primeiro ir ate 11:00 e invadir o das 10:45.
        longo = Servico.objects.create(nome="Barba", duracao_minutos=15, preco=20)
        primeiro = self.criar(self.base)
        self.criar(self.base + timedelta(minutes=45), cliente=self.outro_cliente, servico=longo)

        resposta = self.editar_duracao(self.corte, 60)

        self.assertContains(resposta, "Nao e possivel mudar a duracao")
        self.corte.refresh_from_db()
        primeiro.refresh_from_db()
        self.assertEqual(self.corte.duracao_minutos, 30)
        self.assertEqual(primeiro.fim, self.base + timedelta(minutes=30))

    # --- situacao na criacao ---

    def test_formulario_novo_nao_mostra_o_campo_situacao(self):
        resposta = self.client.get(reverse("agendamento_novo"))

        self.assertNotContains(resposta, 'name="status"')

    def test_agendamento_novo_sempre_nasce_agendado(self):
        self.client.post(reverse("agendamento_novo"), self.dados_form(self.base, status="cancelado"))

        self.assertEqual(Agendamento.objects.get().status, Agendamento.Status.AGENDADO)

    def test_formulario_de_edicao_mantem_o_campo_situacao(self):
        ag = self.criar(self.base)

        resposta = self.client.get(reverse("agendamento_editar", args=[ag.pk]))

        self.assertContains(resposta, 'name="status"')

    # --- ordem da lista ---

    def test_lista_mostra_primeiro_o_horario_mais_proximo(self):
        longe = self.criar(self.base + timedelta(days=5), cliente=self.outro_cliente)
        perto = self.criar(self.base)
        passado = self.criar(self.base - timedelta(days=10))

        resposta = self.client.get(reverse("agendamento_lista"))

        self.assertEqual(list(resposta.context["agendamentos"]), [perto, longe, passado])
