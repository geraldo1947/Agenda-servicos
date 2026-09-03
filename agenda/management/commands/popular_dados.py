from django.core.management.base import BaseCommand

from agenda.models import Cliente, Servico


class Command(BaseCommand):
    """Cria dados de exemplo para gravar o video sem digitar tudo na mao.

    Uso: python manage.py popular_dados
    """

    help = "Cria clientes e servicos de exemplo."

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

    def handle(self, *args, **options):
        for nome, telefone, email in self.CLIENTES:
            Cliente.objects.get_or_create(nome=nome, defaults={"telefone": telefone, "email": email})

        for nome, descricao, duracao, preco in self.SERVICOS:
            Servico.objects.get_or_create(
                nome=nome,
                defaults={"descricao": descricao, "duracao_minutos": duracao, "preco": preco},
            )

        self.stdout.write(self.style.SUCCESS("Dados de exemplo criados."))
