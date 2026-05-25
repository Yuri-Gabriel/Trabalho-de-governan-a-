from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("avaliacao", "0006_alter_pdti_objetivos_estrategicos_texto"),
    ]

    operations = [
        migrations.AddField(
            model_name="pdti",
            name="diagnostico_samti",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="pdti",
            name="analise_de_riscos",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="pdti",
            name="visao_de_futuro",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="pdti",
            name="conclusao",
            field=models.TextField(blank=True),
        ),
    ]
