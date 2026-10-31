import calendar
from datetime import date, datetime, time, timedelta
from decimal import Decimal

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db.models import Count, ProtectedError, Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import AgendamentoForm, ClienteForm, ServicoForm
from .models import Agendamento, Cliente, Servico


def home(request):
    """Tela inicial com os numeros do sistema e os proximos horarios."""
    agendamentos_futuros = Agendamento.objects.filter(
        status=Agendamento.Status.AGENDADO, inicio__gte=timezone.now()
    )
    contexto = {
        "total_clientes": Cliente.objects.count(),
        "total_servicos": Servico.objects.filter(ativo=True).count(),
        "total_agendamentos": agendamentos_futuros.count(),
        "proximos": agendamentos_futuros.select_related("cliente", "servico")[:5],
    }
    return render(request, "agenda/home.html", contexto)


# --------------------------------------------------------------------------
# Clientes
# --------------------------------------------------------------------------

def cliente_lista(request):
    busca = request.GET.get("q", "").strip()
    clientes = Cliente.objects.all()
    if busca:
        # Q() permite combinar condicoes com OU: nome OU telefone.
        clientes = clientes.filter(Q(nome__icontains=busca) | Q(telefone__icontains=busca))
    return render(request, "agenda/cliente_lista.html", {"clientes": clientes, "busca": busca})


def cliente_novo(request):
    form = ClienteForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Cliente cadastrado com sucesso.")
        return redirect("cliente_lista")
    return render(request, "agenda/form.html", {"form": form, "voltar": "cliente_lista", "titulo": "Novo cliente"})


def cliente_editar(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    form = ClienteForm(request.POST or None, instance=cliente)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Cliente atualizado com sucesso.")
        return redirect("cliente_lista")
    return render(request, "agenda/form.html", {"form": form, "voltar": "cliente_lista", "titulo": "Editar cliente"})


def cliente_excluir(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    # So apaga no POST: um GET nunca pode alterar dados (link de robo, prefetch...).
    if request.method == "POST":
        try:
            cliente.delete()
        except ProtectedError:
            # O cliente tem agendamentos (on_delete=PROTECT no model).
            messages.error(request, "Nao e possivel excluir: o cliente possui agendamentos.")
        else:
            messages.success(request, "Cliente excluido.")
        return redirect("cliente_lista")
    return render(request, "agenda/confirmar_exclusao.html", {"objeto": cliente, "voltar": "cliente_lista"})


# --------------------------------------------------------------------------
# Servicos
# --------------------------------------------------------------------------

def servico_lista(request):
    busca = request.GET.get("q", "").strip()
    servicos = Servico.objects.all()
    if busca:
        servicos = servicos.filter(nome__icontains=busca)
    return render(request, "agenda/servico_lista.html", {"servicos": servicos, "busca": busca})


def servico_novo(request):
    form = ServicoForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Servico cadastrado com sucesso.")
        return redirect("servico_lista")
    return render(request, "agenda/form.html", {"form": form, "voltar": "servico_lista", "titulo": "Novo servico"})


def servico_editar(request, pk):
    servico = get_object_or_404(Servico, pk=pk)
    form = ServicoForm(request.POST or None, instance=servico)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Servico atualizado com sucesso.")
        return redirect("servico_lista")
    return render(request, "agenda/form.html", {"form": form, "voltar": "servico_lista", "titulo": "Editar servico"})


def servico_excluir(request, pk):
    servico = get_object_or_404(Servico, pk=pk)
    if request.method == "POST":
        try:
            servico.delete()
        except ProtectedError:
            messages.error(request, "Nao e possivel excluir: o servico possui agendamentos. Desative-o em vez de excluir.")
        else:
            messages.success(request, "Servico excluido.")
        return redirect("servico_lista")
    return render(request, "agenda/confirmar_exclusao.html", {"objeto": servico, "voltar": "servico_lista"})


# --------------------------------------------------------------------------
# Agendamentos
# --------------------------------------------------------------------------

def agendamento_lista(request):
    data = request.GET.get("data", "").strip()
    status = request.GET.get("status", "").strip()
    agendamentos = Agendamento.objects.select_related("cliente", "servico")
    if data:
        # inicio__date compara so a data (no fuso configurado). Data invalida
        # (digitada na mao na URL) e ignorada em vez de quebrar a pagina.
        try:
            agendamentos = agendamentos.filter(inicio__date=data)
        except (ValueError, ValidationError):
            data = ""
    if status in Agendamento.Status.values:
        agendamentos = agendamentos.filter(status=status)
    else:
        status = ""
    # Os proximos horarios primeiro (do mais proximo para o mais distante);
    # depois os que ja passaram, do mais recente para o mais antigo.
    agora = timezone.now()
    agendamentos = list(agendamentos.filter(inicio__gte=agora).order_by("inicio")) + list(
        agendamentos.filter(inicio__lt=agora).order_by("-inicio")
    )
    contexto = {
        "agendamentos": agendamentos,
        "data": data,
        "status": status,
        "opcoes_status": Agendamento.Status.choices,
    }
    return render(request, "agenda/agendamento_lista.html", contexto)


def agendamento_novo(request):
    form = AgendamentoForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        # is_valid() ja rodou o clean() do model, que checa conflito de horario.
        form.save()
        messages.success(request, "Agendamento criado com sucesso.")
        return redirect("agendamento_lista")
    return render(request, "agenda/form.html", {"form": form, "voltar": "agendamento_lista", "titulo": "Novo agendamento"})


def agendamento_editar(request, pk):
    agendamento = get_object_or_404(Agendamento, pk=pk)
    form = AgendamentoForm(request.POST or None, instance=agendamento)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Agendamento atualizado com sucesso.")
        return redirect("agendamento_lista")
    return render(request, "agenda/form.html", {"form": form, "voltar": "agendamento_lista", "titulo": "Editar agendamento"})


def agendamento_excluir(request, pk):
    agendamento = get_object_or_404(Agendamento, pk=pk)
    if request.method == "POST":
        agendamento.delete()
        messages.success(request, "Agendamento excluido.")
        return redirect("agendamento_lista")
    return render(request, "agenda/confirmar_exclusao.html", {"objeto": agendamento, "voltar": "agendamento_lista"})


# --------------------------------------------------------------------------
# Relatorios
# --------------------------------------------------------------------------

def _ler_data(texto):
    """Converte 'AAAA-MM-DD' em date. Texto vazio ou invalido vira None."""
    try:
        return date.fromisoformat(texto)
    except ValueError:
        return None


def relatorios(request):
    """Resumo do periodo: quantidades, faturamento e rankings.

    So agendamentos CONCLUIDOS contam como faturamento (o servico foi feito);
    os AGENDADOS aparecem como "a receber" e os CANCELADOS ficam de fora.
    """
    hoje = timezone.localdate()
    primeiro_do_mes = hoje.replace(day=1)
    ultimo_do_mes = hoje.replace(day=calendar.monthrange(hoje.year, hoje.month)[1])

    texto_inicio = request.GET.get("inicio", "").strip()
    texto_fim = request.GET.get("fim", "").strip()
    inicio = _ler_data(texto_inicio)
    fim = _ler_data(texto_fim)

    # Data digitada na mao na URL e invalida: avisa e volta para o mes atual.
    if (texto_inicio and not inicio) or (texto_fim and not fim):
        messages.warning(request, "Data invalida: mostrando o mes atual.")
        inicio = fim = None
    inicio = inicio or primeiro_do_mes
    fim = fim or ultimo_do_mes
    if fim < inicio:
        messages.warning(request, "A data final e anterior a inicial: mostrando o mes atual.")
        inicio, fim = primeiro_do_mes, ultimo_do_mes

    # O dia final entra inteiro: o filtro vai ate a meia-noite do dia seguinte.
    fuso = timezone.get_current_timezone()
    comeco = timezone.make_aware(datetime.combine(inicio, time.min), fuso)
    limite = timezone.make_aware(datetime.combine(fim + timedelta(days=1), time.min), fuso)
    periodo = Agendamento.objects.filter(inicio__gte=comeco, inicio__lt=limite)

    concluido = Q(status=Agendamento.Status.CONCLUIDO)
    agendado = Q(status=Agendamento.Status.AGENDADO)
    cancelado = Q(status=Agendamento.Status.CANCELADO)
    resumo = periodo.aggregate(
        total=Count("pk"),
        concluidos=Count("pk", filter=concluido),
        agendados=Count("pk", filter=agendado),
        cancelados=Count("pk", filter=cancelado),
        faturamento=Sum("servico__preco", filter=concluido),
        a_receber=Sum("servico__preco", filter=agendado),
    )
    # Sum devolve None quando nao ha linhas; no relatorio isso e R$ 0,00.
    resumo["faturamento"] = resumo["faturamento"] or Decimal("0")
    resumo["a_receber"] = resumo["a_receber"] or Decimal("0")
    resumo["taxa_cancelamento"] = round(100 * resumo["cancelados"] / resumo["total"]) if resumo["total"] else 0

    # Rankings ignoram cancelados (nao aconteceram). Agrupa pelo id e nao pelo
    # nome, para dois servicos com o mesmo nome nao virarem uma linha so.
    validos = periodo.exclude(cancelado)
    servicos_top = (
        validos.values("servico_id", "servico__nome")
        .annotate(quantidade=Count("pk"), faturamento=Sum("servico__preco", filter=concluido))
        .order_by("-quantidade", "servico__nome")[:5]
    )
    clientes_top = (
        validos.values("cliente_id", "cliente__nome")
        .annotate(quantidade=Count("pk"), gasto=Sum("servico__preco", filter=concluido))
        .order_by("-quantidade", "cliente__nome")[:5]
    )

    contexto = {
        "inicio": inicio,
        "fim": fim,
        "resumo": resumo,
        "servicos_top": servicos_top,
        "clientes_top": clientes_top,
    }
    return render(request, "agenda/relatorios.html", contexto)
