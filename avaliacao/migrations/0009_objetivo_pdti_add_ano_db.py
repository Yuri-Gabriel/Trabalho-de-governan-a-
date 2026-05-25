from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("avaliacao", "0008_metaindicador_add_ano_conclusao_db"),
    ]

    operations = [
        # O schema legado tem `resultado_esperado_2029`, mas não tinha a coluna `ano`.
        # Esta migration adiciona a coluna faltante no banco.
        migrations.AddField(
            model_name="objetivoestrategicopdti",
            name="ano",
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
    ]
