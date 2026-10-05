import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("inmuebles", "0002_alter_perfil_options_alter_comuna_region_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="TipoInmueble",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("nombre", models.CharField(max_length=50, unique=True)),
                ("descripcion", models.CharField(blank=True, max_length=200, verbose_name="descripción")),
            ],
            options={
                "verbose_name": "tipo de inmueble",
                "verbose_name_plural": "tipos de inmueble",
            },
        ),
        migrations.RemoveField(
            model_name="inmueble",
            name="tipo_inmueble",
        ),
        migrations.AddField(
            model_name="inmueble",
            name="tipo_inmueble",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="inmuebles",
                to="inmuebles.tipoinmueble",
                verbose_name="tipo de inmueble",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="inmueble",
            name="tipo_inmueble",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="inmuebles",
                to="inmuebles.tipoinmueble",
                verbose_name="tipo de inmueble",
            ),
        ),
    ]
