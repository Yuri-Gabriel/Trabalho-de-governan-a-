from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class UserRole(models.TextChoices):
    ADMIN = "ADMIN", "Administrador"
    CONSULTOR = "CONSULTOR", "Consultor/Governança"
    DIRETORIA = "DIRETORIA", "Diretoria/Stakeholder"


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=UserRole.choices, default=UserRole.DIRETORIA)

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"


class Empresa(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="empresas",
        null=True,
        blank=True,
    )
    nome = models.CharField(max_length=150)
    cnpj = models.CharField(max_length=18, blank=True)
    setor = models.CharField(max_length=100, blank=True)
    criada_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome


class CategoriaQuestao(models.Model):
    nome = models.CharField(max_length=120, unique=True)
    descricao = models.TextField(blank=True)

    def __str__(self):
        return self.nome


class Questao(models.Model):
    categoria = models.ForeignKey(CategoriaQuestao, on_delete=models.PROTECT, related_name="questoes")
    texto = models.TextField()
    ativa = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.categoria.nome}: {self.texto[:60]}"


class AvaliacaoStatus(models.TextChoices):
    ABERTA = "ABERTA", "Aberta"
    CONCLUIDA = "CONCLUIDA", "Concluída"


class Avaliacao(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="avaliacoes")
    nome = models.CharField(max_length=150)
    consultor_responsavel = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="avaliacoes_responsavel",
    )
    participantes = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="avaliacoes_participantes")
    status = models.CharField(max_length=20, choices=AvaliacaoStatus.choices, default=AvaliacaoStatus.ABERTA)
    criada_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-criada_em"]

    def __str__(self):
        return f"{self.empresa.nome} - {self.nome}"

    def total_questoes(self):
        return Questao.objects.filter(ativa=True).count()

    def total_respostas(self):
        return self.respostas.count()


class RespostaEscolha(models.TextChoices):
    SIM = "SIM", "Sim"
    NAO = "NAO", "Não"


class Resposta(models.Model):
    avaliacao = models.ForeignKey(Avaliacao, on_delete=models.CASCADE, related_name="respostas")
    questao = models.ForeignKey(Questao, on_delete=models.CASCADE)
    respondido_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    resposta = models.CharField(max_length=3, choices=RespostaEscolha.choices)
    evidencia_descricao = models.TextField(blank=True)
    evidencia_arquivo = models.FileField(upload_to="evidencias/", blank=True)
    providencia = models.TextField(blank=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("avaliacao", "questao")

    def __str__(self):
        return f"{self.avaliacao} / Q{self.questao_id} - {self.resposta}"

    def clean(self):
        if self.resposta == RespostaEscolha.SIM:
            if not self.evidencia_descricao and not self.evidencia_arquivo:
                raise ValidationError("Para resposta SIM, informe descrição ou upload de evidência.")
            self.providencia = ""

        if self.resposta == RespostaEscolha.NAO:
            if not self.providencia:
                raise ValidationError("Para resposta NÃO, informe uma providência/plano de ação.")
            self.evidencia_descricao = ""
            if self.evidencia_arquivo:
                self.evidencia_arquivo = None


class LogAuditoriaResposta(models.Model):
    resposta_registro = models.ForeignKey(Resposta, on_delete=models.CASCADE, related_name="logs")
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    resposta = models.CharField(max_length=3, choices=RespostaEscolha.choices)
    evidencia_descricao = models.TextField(blank=True)
    evidencia_arquivo_nome = models.CharField(max_length=255, blank=True)
    providencia = models.TextField(blank=True)
    criado_em = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-criado_em"]

    def __str__(self):
        return f"Log #{self.id} - {self.usuario} - {self.criado_em:%d/%m/%Y %H:%M}"
