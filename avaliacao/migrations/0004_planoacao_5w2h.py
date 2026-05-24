from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("avaliacao", "0003_roadmap_phase1_phase2"),  # código local
        # Nota: banco usa numeração divergente (0006_fase2_camada_humana_e_backfill_frameworks)
        # Esta migration é aplicada via --fake pois as colunas já existem no banco
    ]

    operations = [
        migrations.AddField(
            model_name="planoacao",
            name="where_local",
            field=models.CharField(blank=True, db_column="where", max_length=255, verbose_name="Where (onde será feito?)"),
        ),
        migrations.AddField(
            model_name="planoacao",
            name="how",
            field=models.TextField(blank=True, verbose_name="How (como será feito?)"),
        ),
        migrations.AddField(
            model_name="planoacao",
            name="how_much",
            field=models.CharField(blank=True, max_length=255, verbose_name="How Much (custo/esforço estimado)"),
        ),
    ]
