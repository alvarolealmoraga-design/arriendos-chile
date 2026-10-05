import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Comuna",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("nombre", models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name="Region",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("nombre", models.CharField(max_length=100, unique=True)),
            ],
            options={
                "verbose_name": "región",
                "verbose_name_plural": "regiones",
            },
        ),
        migrations.CreateModel(
            name="Inmueble",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("nombre", models.CharField(max_length=200)),
                ("descripcion", models.TextField()),
                ("m2_construidos", models.DecimalField(decimal_places=2, max_digits=8)),
                ("m2_totales", models.DecimalField(decimal_places=2, max_digits=8)),
                ("estacionamientos", models.PositiveIntegerField(default=0)),
                ("habitaciones", models.PositiveIntegerField(default=1)),
                ("banos", models.PositiveIntegerField(default=1)),
                ("direccion", models.CharField(max_length=200)),
                (
                    "tipo_inmueble",
                    models.CharField(
                        choices=[
                            ("casa", "Casa"),
                            ("departamento", "Departamento"),
                            ("parcela", "Parcela"),
                        ],
                        max_length=20,
                    ),
                ),
                (
                    "precio_mensual",
                    models.DecimalField(decimal_places=0, max_digits=10),
                ),
                ("disponible", models.BooleanField(default=True)),
                (
                    "comuna",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="inmuebles",
                        to="inmuebles.comuna",
                    ),
                ),
                (
                    "propietario",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="inmuebles",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Perfil",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                (
                    "tipo_usuario",
                    models.CharField(
                        choices=[
                            ("arrendatario", "Arrendatario"),
                            ("arrendador", "Arrendador"),
                        ],
                        default="arrendatario",
                        max_length=20,
                    ),
                ),
                ("rut", models.CharField(max_length=12, unique=True)),
                ("direccion", models.CharField(blank=True, max_length=200)),
                ("telefono", models.CharField(blank=True, max_length=20)),
                (
                    "usuario",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="perfil",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="comuna",
            name="region",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="comunas",
                to="inmuebles.region",
            ),
        ),
    ]
