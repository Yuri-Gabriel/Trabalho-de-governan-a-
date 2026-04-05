from django.urls import path

from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("cadastro/", views.cadastro, name="cadastro"),
    path("empresas/", views.empresa_list, name="empresa_list"),
    path("empresas/nova/", views.empresa_create, name="empresa_create"),
    path("categorias/", views.categoria_list, name="categoria_list"),
    path("categorias/nova/", views.categoria_create, name="categoria_create"),
    path("questoes/", views.questao_list, name="questao_list"),
    path("questoes/nova/", views.questao_create, name="questao_create"),
    path("questoes/<int:questao_id>/editar/", views.questao_update, name="questao_update"),
    path("avaliacoes/", views.avaliacao_list, name="avaliacao_list"),
    path("avaliacoes/nova/", views.avaliacao_create, name="avaliacao_create"),
    path("avaliacoes/<int:avaliacao_id>/", views.avaliacao_detail, name="avaliacao_detail"),
    path(
        "avaliacoes/<int:avaliacao_id>/questoes/<int:questao_id>/",
        views.responder_questao,
        name="responder_questao",
    ),
    path("avaliacoes/<int:avaliacao_id>/relatorio/", views.relatorio, name="relatorio"),
    path("avaliacoes/<int:avaliacao_id>/relatorio/print/", views.relatorio_print, name="relatorio_print"),
    path("avaliacoes/<int:avaliacao_id>/auditoria/", views.auditoria, name="auditoria"),
    path("avaliacoes/<int:avaliacao_id>/concluir/", views.concluir_avaliacao, name="concluir_avaliacao"),
]
