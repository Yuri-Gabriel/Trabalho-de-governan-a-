from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from .models import (
    Avaliacao,
    AvaliacaoStatus,
    CategoriaQuestao,
    Empresa,
    LogAuditoriaResposta,
    Questao,
    Resposta,
    RespostaEscolha,
    UserRole,
)
from .services import gerar_relatorio

User = get_user_model()


class BaseAvaliacaoTestCase(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(username="admin", password="senhaforte123")
        self.admin.profile.role = UserRole.ADMIN
        self.admin.profile.save(update_fields=["role"])

        self.consultor = User.objects.create_user(username="consultor", password="senhaforte123")
        self.consultor.profile.role = UserRole.CONSULTOR
        self.consultor.profile.save(update_fields=["role"])

        self.outro_consultor = User.objects.create_user(username="outro", password="senhaforte123")
        self.outro_consultor.profile.role = UserRole.CONSULTOR
        self.outro_consultor.profile.save(update_fields=["role"])

        self.diretoria = User.objects.create_user(username="diretoria", password="senhaforte123")
        self.diretoria.profile.role = UserRole.DIRETORIA
        self.diretoria.profile.save(update_fields=["role"])

        self.empresa = Empresa.objects.create(nome="Empresa XPTO", cnpj="00.000.000/0001-00", setor="Serviços")
        self.categoria = CategoriaQuestao.objects.create(nome="Governança", descricao="Categoria de teste")
        self.questao = Questao.objects.create(categoria=self.categoria, texto="Existe processo formal?", ativa=True)
        self.avaliacao = Avaliacao.objects.create(
            empresa=self.empresa,
            nome="Diagnóstico 2026",
            consultor_responsavel=self.consultor,
        )
        self.avaliacao.participantes.add(self.consultor, self.diretoria)


class WorkflowAvaliacaoTests(BaseAvaliacaoTestCase):
    def test_avaliacao_concluida_bloqueia_novas_respostas(self):
        self.avaliacao.status = AvaliacaoStatus.CONCLUIDA
        self.avaliacao.save(update_fields=["status"])
        self.client.force_login(self.consultor)

        response = self.client.post(
            reverse("responder_questao", args=[self.avaliacao.id, self.questao.id]),
            {
                "resposta": RespostaEscolha.SIM,
                "evidencia_descricao": "Documento enviado",
                "providencia": "",
            },
        )

        self.assertRedirects(response, reverse("avaliacao_detail", args=[self.avaliacao.id]))
        self.assertFalse(Resposta.objects.filter(avaliacao=self.avaliacao, questao=self.questao).exists())

    def test_somente_consultor_responsavel_ou_admin_ve_auditoria(self):
        resposta = Resposta.objects.create(
            avaliacao=self.avaliacao,
            questao=self.questao,
            respondido_por=self.consultor,
            resposta=RespostaEscolha.NAO,
            providencia="Criar processo",
        )
        LogAuditoriaResposta.objects.create(
            resposta_registro=resposta,
            usuario=self.consultor,
            resposta=RespostaEscolha.NAO,
            providencia="Criar processo",
        )
        self.client.force_login(self.outro_consultor)

        response = self.client.get(reverse("auditoria", args=[self.avaliacao.id]))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("dashboard"))

    def test_somente_consultor_responsavel_pode_concluir(self):
        self.client.force_login(self.outro_consultor)

        response = self.client.post(reverse("concluir_avaliacao", args=[self.avaliacao.id]))

        self.assertRedirects(response, reverse("dashboard"))
        self.avaliacao.refresh_from_db()
        self.assertEqual(self.avaliacao.status, AvaliacaoStatus.ABERTA)

    def test_concluir_avaliacao_rejeita_get(self):
        self.client.force_login(self.consultor)

        response = self.client.get(reverse("concluir_avaliacao", args=[self.avaliacao.id]))

        self.assertEqual(response.status_code, 405)


@override_settings(
    ALLOWED_HOSTS=["testserver", "127.0.0.1", "localhost"],
    CSRF_TRUSTED_ORIGINS=["http://testserver", "https://testserver"],
)
class CsrfProtectionTests(BaseAvaliacaoTestCase):
    def setUp(self):
        super().setUp()
        self.csrf_client = Client(enforce_csrf_checks=True)
        self.csrf_client.force_login(self.consultor)

    def test_responder_questao_post_sem_csrf_retorna_403(self):
        response = self.csrf_client.post(
            reverse("responder_questao", args=[self.avaliacao.id, self.questao.id]),
            {
                "resposta": RespostaEscolha.SIM,
                "evidencia_descricao": "Documento enviado",
                "providencia": "",
            },
        )

        self.assertEqual(response.status_code, 403)

    def test_responder_questao_post_com_csrf_persiste_resposta(self):
        page = self.csrf_client.get(reverse("responder_questao", args=[self.avaliacao.id, self.questao.id]))
        csrf_token = page.cookies["csrftoken"].value

        response = self.csrf_client.post(
            reverse("responder_questao", args=[self.avaliacao.id, self.questao.id]),
            {
                "resposta": RespostaEscolha.SIM,
                "evidencia_descricao": "Documento enviado",
                "providencia": "",
                "csrfmiddlewaretoken": csrf_token,
            },
            HTTP_X_CSRFTOKEN=csrf_token,
        )

        self.assertRedirects(response, reverse("avaliacao_detail", args=[self.avaliacao.id]))
        self.assertTrue(Resposta.objects.filter(avaliacao=self.avaliacao, questao=self.questao).exists())


class CategoriaQuestaoTests(BaseAvaliacaoTestCase):
    def test_admin_pode_criar_categoria_pela_tela(self):
        self.client.force_login(self.admin)

        response = self.client.post(
            reverse("categoria_create"),
            {"nome": "Segurança", "descricao": "Controles e práticas de segurança."},
        )

        self.assertRedirects(response, reverse("categoria_list"))
        self.assertTrue(CategoriaQuestao.objects.filter(nome="Segurança").exists())

    def test_consultor_nao_pode_criar_categoria(self):
        self.client.force_login(self.consultor)

        response = self.client.get(reverse("categoria_create"))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("dashboard"))


class RelatorioMaturidadeTests(BaseAvaliacaoTestCase):
    def test_relatorio_retorna_explicacao_e_recomendacoes(self):
        Resposta.objects.create(
            avaliacao=self.avaliacao,
            questao=self.questao,
            respondido_por=self.consultor,
            resposta=RespostaEscolha.SIM,
            evidencia_descricao="Fluxo documentado",
        )

        dados = gerar_relatorio(self.avaliacao)

        self.assertEqual(dados["classificacao"], "Estratégico")
        self.assertIn("habilitadora estratégica", dados["descricao_maturidade"])
        self.assertTrue(dados["recomendacoes_maturidade"])
