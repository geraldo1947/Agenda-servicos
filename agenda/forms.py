from django import forms
from django.db.models import Q
from django.utils import timezone

from .models import Agendamento, Cliente, Servico


class BootstrapFormMixin:
    """Aplica a classe CSS do Bootstrap em todos os campos.

    Sem isso seria preciso escrever o HTML de cada <input> na mao no template.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for campo in self.fields.values():
            if isinstance(campo.widget, forms.CheckboxInput):
                campo.widget.attrs.setdefault("class", "form-check-input")
            elif isinstance(campo.widget, forms.Select):
                campo.widget.attrs.setdefault("class", "form-select")
            else:
                campo.widget.attrs.setdefault("class", "form-control")


class ClienteForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ["nome", "telefone", "email"]


class ServicoForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Servico
        fields = ["nome", "descricao", "duracao_minutos", "preco", "ativo"]
        widgets = {"descricao": forms.Textarea(attrs={"rows": 3})}


class AgendamentoForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Agendamento
        fields = ["cliente", "servico", "inicio", "status", "observacoes"]
        widgets = {
            # type="datetime-local" mostra o seletor de data e hora do navegador.
            "inicio": forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"),
            "observacoes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # O navegador envia o valor no formato do datetime-local.
        self.fields["inicio"].input_formats = ["%Y-%m-%dT%H:%M"]
        # Servico inativo nao aparece para novos agendamentos. Ao editar,
        # o servico ja escolhido continua na lista mesmo que tenha sido desativado.
        ativos = Q(ativo=True)
        if self.instance.servico_id:
            ativos |= Q(pk=self.instance.servico_id)
        self.fields["servico"].queryset = Servico.objects.filter(ativos)

    def clean_inicio(self):
        inicio = self.cleaned_data["inicio"]
        # Nao permite marcar no passado, mas deixa editar um agendamento antigo
        # sem mudar o horario (para poder marcar como concluido, por exemplo).
        mudou = "inicio" in self.changed_data or not self.instance.pk
        if mudou and inicio < timezone.now():
            raise forms.ValidationError("Escolha uma data e hora no futuro.")
        return inicio
