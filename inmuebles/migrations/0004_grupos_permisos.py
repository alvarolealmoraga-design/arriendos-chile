from django.contrib.auth.management import create_permissions
from django.db import migrations

GRUPOS = {
    "Arrendatarios": [
        "view_region", "view_comuna", "view_tipoinmueble", "view_inmueble",
    ],
    "Arrendadores": [
        "view_region", "view_comuna", "view_tipoinmueble",
        "view_inmueble", "add_inmueble", "change_inmueble", "delete_inmueble",
    ],
    "Administradores": [
        "view_region", "add_region", "change_region", "delete_region",
        "view_comuna", "add_comuna", "change_comuna", "delete_comuna",
        "view_tipoinmueble", "add_tipoinmueble", "change_tipoinmueble", "delete_tipoinmueble",
        "view_inmueble", "add_inmueble", "change_inmueble", "delete_inmueble",
        "view_perfil", "change_perfil",
    ],
}


def crear_grupos(apps, schema_editor):
    for app_config in apps.get_app_configs():
        app_config.models_module = True
        create_permissions(app_config, apps=apps, verbosity=0)
        app_config.models_module = None

    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")
    for nombre, codenames in GRUPOS.items():
        grupo, _ = Group.objects.get_or_create(name=nombre)
        permisos = Permission.objects.filter(content_type__app_label="inmuebles", codename__in=codenames)
        grupo.permissions.set(permisos)


def eliminar_grupos(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Group.objects.filter(name__in=GRUPOS.keys()).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("inmuebles", "0003_tipoinmueble"),
        ("auth", "0012_alter_user_first_name_max_length"),
        ("contenttypes", "0002_remove_content_type_name"),
    ]

    operations = [
        migrations.RunPython(crear_grupos, eliminar_grupos),
    ]
