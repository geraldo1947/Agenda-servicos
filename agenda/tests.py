from django.test import TestCase
from django.urls import reverse

from .models import Cliente, Servico


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
