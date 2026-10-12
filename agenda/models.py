from django.db import models


class Cliente(models.Model):
    """Pessoa que marca um horario. Entidade central da AC1."""

    nome = models.CharField("nome", max_length=120)
    telefone = models.CharField("telefone", max_length=20)
    email = models.EmailField("e-mail", blank=True)
    criado_em = models.DateTimeField("criado em", auto_now_add=True)

    class Meta:
        verbose_name = "cliente"
        verbose_name_plural = "clientes"
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class Servico(models.Model):
    """Servico oferecido pelo estabelecimento (corte, manicure, consulta...)."""

    nome = models.CharField("nome", max_length=120)
    descricao = models.TextField("descricao", blank=True)
    # A duracao existe desde a AC1 porque a AC2 vai usar ela para calcular
    # o fim do agendamento e detectar conflito de horario.
    duracao_minutos = models.PositiveIntegerField("duracao (minutos)", default=30)
    preco = models.DecimalField("preco", max_digits=8, decimal_places=2)
    ativo = models.BooleanField("ativo", default=True)
    criado_em = models.DateTimeField("criado em", auto_now_add=True)

    class Meta:
        verbose_name = "servico"
        verbose_name_plural = "servicos"
        ordering = ["nome"]

    def __str__(self):
        return f"{self.nome} ({self.duracao_minutos} min)"
