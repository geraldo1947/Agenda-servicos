from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from agenda.models import Agendamento, Cliente, Servico


class Command(BaseCommand):
    """Cria dados de exemplo para gravar o video sem digitar tudo na mao.

    Uso: python manage.py popular_dados
    """

    help = "Cria clientes, servicos e agendamentos de exemplo."

    CLIENTES = [
        ("Maria Silva", "27 99999-1111", "maria@exemplo.com"),
        ("Joao Souza", "27 99999-2222", "joao@exemplo.com"),
        ("Ana Pereira", "27 99999-3333", ""),
    ]

    SERVICOS = [
        ("Corte de cabelo", "Corte masculino ou feminino", 30, "50.00"),
        ("Coloracao", "Aplicacao de tintura", 90, "180.00"),
        ("Manicure", "", 45, "40.00"),
    ]

    # (cliente, servico, dias a partir de hoje, hora, minuto)
    AGENDAMENTOS = [
        ("Maria Silva", "Corte de cabelo", 1, 9, 0),
        ("Joao Souza", "Coloracao", 1, 10, 0),
        ("Ana Pereira", "Manicure", 2, 14, 30),
    ]

    def handle(self, *args, **options):
        for nome, telefone, email in self.CLIENTES:
            Cliente.objects.get_or_create(nome=nome, defaults={"telefone": telefone, "email": email})

        for nome, descricao, duracao, preco in self.SERVICOS:
            Servico.objects.get_or_create(
                nome=nome,
                defaults={"descricao": descricao, "duracao_minutos": duracao, "preco": preco},
            )

        # Os horarios dependem do dia em que o comando roda. Por isso so cria
        # agendamentos se ainda nao existir nenhum (rodar de novo nao duplica).
        agendamentos = [] if Agendamento.objects.exists() else self.AGENDAMENTOS

        for nome_cliente, nome_servico, dias, hora, minuto in agendamentos:
            inicio = (timezone.localtime() + timedelta(days=dias)).replace(
                hour=hora, minute=minuto, second=0, microsecond=0
            )
            cliente = Cliente.objects.get(nome=nome_cliente)
            servico = Servico.objects.get(nome=nome_servico)
            Agendamento.objects.create(cliente=cliente, servico=servico, inicio=inicio)

        self.stdout.write(self.style.SUCCESS("Dados de exemplo criados."))
