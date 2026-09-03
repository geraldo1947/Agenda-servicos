from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ClienteForm, ServicoForm
from .models import Cliente, Servico


def home(request):
    """Tela inicial com os numeros do sistema."""
    contexto = {
        "total_clientes": Cliente.objects.count(),
        "total_servicos": Servico.objects.filter(ativo=True).count(),
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
    return render(request, "agenda/form.html", {"form": form, "titulo": "Novo cliente"})


def cliente_editar(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    form = ClienteForm(request.POST or None, instance=cliente)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Cliente atualizado com sucesso.")
        return redirect("cliente_lista")
    return render(request, "agenda/form.html", {"form": form, "titulo": "Editar cliente"})


def cliente_excluir(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    # So apaga no POST: um GET nunca pode alterar dados (link de robo, prefetch...).
    if request.method == "POST":
        cliente.delete()
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
    return render(request, "agenda/form.html", {"form": form, "titulo": "Novo servico"})


def servico_editar(request, pk):
    servico = get_object_or_404(Servico, pk=pk)
    form = ServicoForm(request.POST or None, instance=servico)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Servico atualizado com sucesso.")
        return redirect("servico_lista")
    return render(request, "agenda/form.html", {"form": form, "titulo": "Editar servico"})


def servico_excluir(request, pk):
    servico = get_object_or_404(Servico, pk=pk)
    if request.method == "POST":
        servico.delete()
        messages.success(request, "Servico excluido.")
        return redirect("servico_lista")
    return render(request, "agenda/confirmar_exclusao.html", {"objeto": servico, "voltar": "servico_lista"})
