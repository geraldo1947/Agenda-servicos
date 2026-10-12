from datetime import timedelta

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


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
    # Minimo de 1 minuto: duracao 0 geraria um horario que nao ocupa tempo.
    duracao_minutos = models.PositiveIntegerField(
        "duracao (minutos)", default=30, validators=[MinValueValidator(1)]
    )
    preco = models.DecimalField("preco", max_digits=8, decimal_places=2)
    ativo = models.BooleanField("ativo", default=True)
    criado_em = models.DateTimeField("criado em", auto_now_add=True)

    class Meta:
        verbose_name = "servico"
        verbose_name_plural = "servicos"
        ordering = ["nome"]

    def __str__(self):
        return f"{self.nome} ({self.duracao_minutos} min)"

    def _duracao_mudou(self):
        """True se este servico ja existe no banco com outra duracao."""
        if not self.pk:
            return False
        antiga = Servico.objects.filter(pk=self.pk).values_list("duracao_minutos", flat=True).first()
        return antiga is not None and antiga != self.duracao_minutos

    def _agendamentos_futuros(self):
        """Agendamentos ativos deste servico que ainda vao acontecer."""
        return (
            self.agendamentos
            .exclude(status=Agendamento.Status.CANCELADO)
            .filter(inicio__gte=timezone.now())
        )

    def clean(self):
        # Mudar a duracao muda o fim dos agendamentos futuros deste servico.
        # Se algum passaria a invadir outro horario, a mudanca e recusada.
        if not self._duracao_mudou():
            return

        nova = timedelta(minutes=self.duracao_minutos)
        for ag in self._agendamentos_futuros().select_related("cliente"):
            invadido = (
                Agendamento.objects
                .exclude(status=Agendamento.Status.CANCELADO)
                .exclude(pk=ag.pk)
                .filter(inicio__lt=ag.inicio + nova, fim__gt=ag.inicio)
                .first()
            )
            if invadido:
                inicio = timezone.localtime(ag.inicio)
                raise ValidationError(
                    f"Nao e possivel mudar a duracao: o agendamento de {ag.cliente.nome} "
                    f"em {inicio:%d/%m/%Y %H:%M} passaria a invadir outro horario."
                )

    def save(self, *args, **kwargs):
        duracao_mudou = self._duracao_mudou()
        super().save(*args, **kwargs)
        if duracao_mudou:
            # Mantem o fim gravado em dia com a nova duracao (so os futuros:
            # o historico ja aconteceu com a duracao antiga).
            nova = timedelta(minutes=self.duracao_minutos)
            for ag in self._agendamentos_futuros():
                ag.fim = ag.inicio + nova
                ag.save(update_fields=["fim"])


class Agendamento(models.Model):
    """Horario marcado: um cliente, um servico, um inicio e um fim.

    Entidade central da AC2. A regra de negocio principal fica aqui no model
    (metodo clean): dois agendamentos nao podem ocupar o mesmo horario.
    """

    class Status(models.TextChoices):
        AGENDADO = "agendado", "Agendado"
        CONCLUIDO = "concluido", "Concluido"
        CANCELADO = "cancelado", "Cancelado"

    # PROTECT: nao deixa apagar um cliente/servico que ja tem agendamento,
    # senao o historico seria apagado junto sem ninguem perceber.
    cliente = models.ForeignKey(Cliente, verbose_name="cliente", on_delete=models.PROTECT, related_name="agendamentos")
    servico = models.ForeignKey(Servico, verbose_name="servico", on_delete=models.PROTECT, related_name="agendamentos")
    inicio = models.DateTimeField("inicio")
    # O fim e calculado no save() (inicio + duracao do servico) e guardado no
    # banco para a busca de conflitos virar uma consulta simples.
    fim = models.DateTimeField("fim", editable=False)
    status = models.CharField("situacao", max_length=10, choices=Status.choices, default=Status.AGENDADO)
    observacoes = models.TextField("observacoes", blank=True)
    criado_em = models.DateTimeField("criado em", auto_now_add=True)

    class Meta:
        verbose_name = "agendamento"
        verbose_name_plural = "agendamentos"
        ordering = ["inicio"]

    def __str__(self):
        return f"{self.cliente} - {self.servico.nome} em {timezone.localtime(self.inicio):%d/%m/%Y %H:%M}"

    def calcular_fim(self):
        """Fim = inicio + duracao do servico."""
        return self.inicio + timedelta(minutes=self.servico.duracao_minutos)

    def conflitos(self):
        """Agendamentos ativos que se sobrepoem a este (exceto ele mesmo).

        Dois intervalos se sobrepoem quando cada um comeca ANTES do outro
        terminar. Se um termina exatamente na hora em que o outro comeca,
        nao ha conflito (10:00-10:30 e 10:30-11:00 podem coexistir).
        Cancelados nao ocupam horario.
        """
        return (
            Agendamento.objects
            .exclude(status=self.Status.CANCELADO)
            .exclude(pk=self.pk)
            .filter(inicio__lt=self.calcular_fim(), fim__gt=self.inicio)
        )

    def clean(self):
        # Se faltou servico ou inicio, o proprio formulario ja mostra o erro do
        # campo; aqui so validamos quando tem tudo para calcular.
        if not (self.servico_id and self.inicio):
            return

        if self.status != self.Status.CANCELADO:
            conflito = self.conflitos().select_related("cliente", "servico").first()
            if conflito:
                inicio = timezone.localtime(conflito.inicio)
                fim = timezone.localtime(conflito.fim)
                raise ValidationError(
                    f"Horario indisponivel: ja existe {conflito.servico.nome} para "
                    f"{conflito.cliente.nome} das {inicio:%H:%M} as {fim:%H:%M} "
                    f"({inicio:%d/%m/%Y})."
                )

    def save(self, *args, **kwargs):
        self.fim = self.calcular_fim()
        super().save(*args, **kwargs)
