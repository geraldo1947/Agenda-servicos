from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),

    path("clientes/", views.cliente_lista, name="cliente_lista"),
    path("clientes/novo/", views.cliente_novo, name="cliente_novo"),
    path("clientes/<int:pk>/editar/", views.cliente_editar, name="cliente_editar"),
    path("clientes/<int:pk>/excluir/", views.cliente_excluir, name="cliente_excluir"),

    path("servicos/", views.servico_lista, name="servico_lista"),
    path("servicos/novo/", views.servico_novo, name="servico_novo"),
    path("servicos/<int:pk>/editar/", views.servico_editar, name="servico_editar"),
    path("servicos/<int:pk>/excluir/", views.servico_excluir, name="servico_excluir"),

    path("agendamentos/", views.agendamento_lista, name="agendamento_lista"),
    path("agendamentos/novo/", views.agendamento_novo, name="agendamento_novo"),
    path("agendamentos/<int:pk>/editar/", views.agendamento_editar, name="agendamento_editar"),
    path("agendamentos/<int:pk>/excluir/", views.agendamento_excluir, name="agendamento_excluir"),
]
