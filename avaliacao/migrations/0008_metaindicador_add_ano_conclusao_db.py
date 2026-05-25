from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("avaliacao", "0007_pdti_add_campos_faltantes"),
    ]

    operations = [
        # O schema legado tinha `meta_2029` mas não tinha a coluna `ano_conclusao`.
        # Esta migration adiciona a coluna faltante no banco.
        migrations.AddField(
            model_name="metaindicador",
            name="ano_conclusao",
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
    ]
