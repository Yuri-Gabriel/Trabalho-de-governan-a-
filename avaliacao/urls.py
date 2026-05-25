from django.urls import path

from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
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
    path(
        "avaliacoes/<int:avaliacao_id>/planos/<int:resposta_id>/",
        views.plano_acao_update,
        name="plano_acao_update",
    ),
    path("avaliacoes/<int:avaliacao_id>/riscos/", views.matriz_risco, name="matriz_risco"),
    path("avaliacoes/<int:avaliacao_id>/riscos/novo/", views.risco_create, name="risco_create"),
    path("avaliacoes/<int:avaliacao_id>/relatorio/", views.relatorio, name="relatorio"),
    path("avaliacoes/<int:avaliacao_id>/api/relatorio/", views.api_relatorio, name="api_relatorio"),
    path("avaliacoes/<int:avaliacao_id>/auditoria/", views.auditoria, name="auditoria"),
    path("avaliacoes/<int:avaliacao_id>/concluir/", views.concluir_avaliacao, name="concluir_avaliacao"),
    path("avaliacoes/<int:avaliacao_id>/plano-acao/", views.plano_acao_5w2h, name="plano_acao_5w2h"),
    path("avaliacoes/<int:avaliacao_id>/plano-acao/exportar/", views.exportar_plano_xlsx, name="exportar_plano_xlsx"),
    path("avaliacoes/<int:avaliacao_id>/relatorio/pdf/", views.exportar_relatorio_pdf, name="exportar_relatorio_pdf"),

    path("empresas/<int:empresa_id>/metas-2029/", views.metas_2029_list, name="metas_2029_list"),
    path("empresas/<int:empresa_id>/metas-2029/nova/", views.metas_2029_create, name="metas_2029_create"),
    path("empresas/<int:empresa_id>/metas-2029/<int:meta_id>/editar/", views.metas_2029_update, name="metas_2029_update"),
    path("empresas/<int:empresa_id>/metas-2029/<int:meta_id>/excluir/", views.metas_2029_delete, name="metas_2029_delete"),

    path("avaliacoes/<int:avaliacao_id>/pdti/", views.pdti_view, name="pdti_view"),
    path("avaliacoes/<int:avaliacao_id>/pdti/pdf/", views.exportar_pdti_pdf, name="exportar_pdti_pdf"),
]
