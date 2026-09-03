from django import forms

from .models import Cliente, Servico


class BootstrapFormMixin:
    """Aplica a classe CSS do Bootstrap em todos os campos.

    Sem isso seria preciso escrever o HTML de cada <input> na mao no template.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for campo in self.fields.values():
            if isinstance(campo.widget, forms.CheckboxInput):
                campo.widget.attrs.setdefault("class", "form-check-input")
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
