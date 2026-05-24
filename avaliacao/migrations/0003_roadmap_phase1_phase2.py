from django.conf import settings
from django.db import migrations, models
import django.core.validators
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("avaliacao", "0002_seed_perguntas_pdf"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="questao",
            name="framework_origem",
            field=models.CharField(
                choices=[
                    ("COBIT5", "COBIT 5"),
                    ("ITIL4", "ITIL 4"),
                    ("ISO27000", "ISO/IEC 27000"),
                    ("ISO31000", "ISO 31000"),
                    ("INTERNO", "Modelo interno"),
                ],
                default="INTERNO",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="questao",
            name="peso",
            field=models.PositiveSmallIntegerField(
                default=1,
                validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)],
            ),
        ),
        migrations.AddField(
            model_name="questao",
            name="referencia",
            field=models.CharField(
                blank=True,
                help_text="Ex.: DSS02 (COBIT), 5.2.3 (ISO), Practice Incident Management (ITIL)",
                max_length=120,
            ),
        ),
        migrations.CreateModel(
            name="RiscoAvaliacao",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("titulo", models.CharField(max_length=180)),
                ("descricao", models.TextField(blank=True)),
                (
                    "impacto",
                    models.PositiveSmallIntegerField(
                        default=3,
                        validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)],
                    ),
                ),
                (
                    "probabilidade",
                    models.PositiveSmallIntegerField(
                        default=3,
                        validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)],
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[("ABERTO", "Aberto"), ("MITIGADO", "Mitigado"), ("ACEITO", "Aceito")],
                        default="ABERTO",
                        max_length=20,
                    ),
                ),
                ("plano_mitigacao", models.TextField(blank=True)),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
                ("atualizado_em", models.DateTimeField(auto_now=True)),
                (
                    "avaliacao",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="riscos",
                        to="avaliacao.avaliacao",
                    ),
                ),
                (
                    "responsavel",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="riscos_responsavel",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-criado_em"],
            },
        ),
        migrations.CreateModel(
            name="PlanoAcao",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("data_limite", models.DateField(blank=True, null=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("ABERTO", "Aberto"),
                            ("EM_ANDAMENTO", "Em andamento"),
                            ("CONCLUIDO", "Concluído"),
                        ],
                        default="ABERTO",
                        max_length=20,
                    ),
                ),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
                ("atualizado_em", models.DateTimeField(auto_now=True)),
                (
                    "resposta",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="plano_acao",
                        to="avaliacao.resposta",
                    ),
                ),
                (
                    "responsavel",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="planos_acao",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["status", "data_limite", "-atualizado_em"],
            },
        ),
    ]