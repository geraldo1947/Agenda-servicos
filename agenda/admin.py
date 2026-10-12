from django.contrib import admin

from .models import Agendamento, Cliente, Servico

admin.site.site_header = "Agenda de Servicos"
admin.site.site_title = "Agenda de Servicos"
admin.site.index_title = "Painel administrativo"


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ["nome", "telefone", "email", "criado_em"]
    search_fields = ["nome", "telefone", "email"]


@admin.register(Servico)
class ServicoAdmin(admin.ModelAdmin):
    list_display = ["nome", "duracao_minutos", "preco", "ativo"]
    list_filter = ["ativo"]
    search_fields = ["nome"]


@admin.register(Agendamento)
class AgendamentoAdmin(admin.ModelAdmin):
    list_display = ["cliente", "servico", "inicio", "fim", "status"]
    list_filter = ["status", "servico"]
    search_fields = ["cliente__nome", "servico__nome"]
    date_hierarchy = "inicio"
