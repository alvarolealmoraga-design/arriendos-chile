from django.contrib.auth.models import Group, User
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from inmuebles.models import Comuna, Inmueble, TipoInmueble


class AutenticacionTest(TestCase):
    def setUp(self):
        call_command("loaddata", "regiones_comunas", "tipos_inmueble", verbosity=0)

    def registrar(self, username="nuevo", tipo="arrendatario", rut="12.345.678-9"):
        return self.client.post(reverse("registro"), {
            "username": username,
            "first_name": "Ana",
            "last_name": "Lagos",
            "email": f"{username}@mail.com",
            "rut": rut,
            "telefono": "",
            "tipo_usuario": tipo,
            "password1": "Arriendo.Seguro#2026",
            "password2": "Arriendo.Seguro#2026",
        })

    def test_apps_instaladas(self):
        from django.conf import settings
        self.assertIn("django.contrib.auth", settings.INSTALLED_APPS)
        self.assertIn("django.contrib.contenttypes", settings.INSTALLED_APPS)

    def test_grupos_creados_por_migracion(self):
        self.assertEqual(Group.objects.filter(name__in=["Arrendatarios", "Arrendadores", "Administradores"]).count(), 3)

    def test_formulario_registro_se_muestra(self):
        respuesta = self.client.get(reverse("registro"))
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, "Crear cuenta")

    def test_registro_crea_usuario_perfil_y_grupo(self):
        respuesta = self.registrar()
        self.assertRedirects(respuesta, reverse("perfil"))
        usuario = User.objects.get(username="nuevo")
        self.assertEqual(usuario.perfil.tipo_usuario, "arrendatario")
        self.assertTrue(usuario.groups.filter(name="Arrendatarios").exists())
        self.assertEqual(int(self.client.session["_auth_user_id"]), usuario.id)

    def test_registro_con_contrasenas_distintas_falla(self):
        respuesta = self.client.post(reverse("registro"), {
            "username": "malo", "first_name": "A", "last_name": "B", "email": "malo@mail.com",
            "rut": "1-9", "tipo_usuario": "arrendatario",
            "password1": "Arriendo.Seguro#2026", "password2": "otra",
        })
        self.assertEqual(respuesta.status_code, 200)
        self.assertFalse(User.objects.filter(username="malo").exists())

    def test_login_y_logout(self):
        self.registrar()
        self.client.post(reverse("logout"))
        respuesta = self.client.post(reverse("login"), {"username": "nuevo", "password": "Arriendo.Seguro#2026"})
        self.assertRedirects(respuesta, reverse("perfil"))
        self.assertIn("_auth_user_id", self.client.session)
        respuesta = self.client.post(reverse("logout"))
        self.assertContains(respuesta, "Sesión cerrada")
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_login_incorrecto(self):
        respuesta = self.client.post(reverse("login"), {"username": "nadie", "password": "x"})
        self.assertContains(respuesta, "incorrectos")

    def test_anonimo_es_redirigido_al_login(self):
        respuesta = self.client.get(reverse("listado_inmuebles"))
        self.assertRedirects(respuesta, reverse("login") + "?next=" + reverse("listado_inmuebles"))

    def test_arrendatario_ve_listado_pero_no_publica(self):
        self.registrar()
        self.assertEqual(self.client.get(reverse("listado_inmuebles")).status_code, 200)
        self.assertEqual(self.client.get(reverse("publicar_inmueble")).status_code, 403)

    def test_arrendador_publica_inmueble(self):
        self.registrar(username="dueno", tipo="arrendador")
        self.assertEqual(self.client.get(reverse("publicar_inmueble")).status_code, 200)
        respuesta = self.client.post(reverse("publicar_inmueble"), {
            "nombre": "Depto Ñuñoa", "descripcion": "Depto nuevo", "direccion": "Irarrázaval 100",
            "tipo_inmueble": TipoInmueble.objects.get(nombre="Departamento").id,
            "comuna": Comuna.objects.get(nombre="Ñuñoa").id,
            "m2_construidos": 50, "m2_totales": 55, "habitaciones": 2, "banos": 1,
            "estacionamientos": 1, "precio_mensual": 500000,
        })
        self.assertRedirects(respuesta, reverse("mis_inmuebles"))
        self.assertEqual(Inmueble.objects.get(nombre="Depto Ñuñoa").propietario.username, "dueno")


class PerfilTest(TestCase):
    def setUp(self):
        call_command("loaddata", "regiones_comunas", "tipos_inmueble", "usuarios", "inmuebles", verbosity=0)

    def entrar(self, username):
        self.client.login(username=username, password="clave1234")

    def test_perfil_requiere_login(self):
        respuesta = self.client.get(reverse("perfil"))
        self.assertRedirects(respuesta, reverse("login") + "?next=" + reverse("perfil"))

    def test_inicio_redirige_al_perfil_si_hay_sesion(self):
        self.entrar("psoto")
        self.assertRedirects(self.client.get(reverse("inicio")), reverse("perfil"))

    def test_redireccion_mi_cuenta(self):
        self.entrar("psoto")
        self.assertRedirects(self.client.get("/mi-cuenta/"), reverse("perfil"))

    def test_perfil_arrendatario_muestra_sus_datos(self):
        self.entrar("psoto")
        respuesta = self.client.get(reverse("perfil"))
        self.assertContains(respuesta, "Pedro Soto")
        self.assertContains(respuesta, "33.333.333-3")
        self.assertContains(respuesta, "Arrendatario")
        self.assertNotContains(respuesta, "Mis inmuebles")

    def test_perfil_arrendador_muestra_resumen(self):
        self.entrar("jperez")
        respuesta = self.client.get(reverse("perfil"))
        self.assertContains(respuesta, "Publicados: 7")
        self.assertContains(respuesta, "Arrendados: 1")

    def test_modificar_datos_personales(self):
        self.entrar("psoto")
        respuesta = self.client.post(reverse("editar_perfil"), {
            "first_name": "Pedro Pablo", "last_name": "Soto", "email": "pedro.soto@mail.com",
            "telefono": "+56900000000", "direccion": "Los Leones 100, Providencia",
        })
        self.assertRedirects(respuesta, reverse("perfil"))
        usuario = User.objects.get(username="psoto")
        self.assertEqual(usuario.first_name, "Pedro Pablo")
        self.assertEqual(usuario.email, "pedro.soto@mail.com")
        self.assertEqual(usuario.perfil.direccion, "Los Leones 100, Providencia")

    def test_no_puede_usar_correo_de_otro(self):
        self.entrar("psoto")
        respuesta = self.client.post(reverse("editar_perfil"), {
            "first_name": "Pedro", "last_name": "Soto", "email": "jperez@mail.com",
            "telefono": "", "direccion": "",
        })
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, "Ya existe otro usuario con este correo.")

    def test_arrendador_edita_y_elimina_su_inmueble(self):
        self.entrar("jperez")
        inmueble = Inmueble.objects.get(nombre="Depto Providencia")
        datos = {
            "nombre": inmueble.nombre, "descripcion": inmueble.descripcion, "direccion": inmueble.direccion,
            "tipo_inmueble": inmueble.tipo_inmueble_id, "comuna": inmueble.comuna_id,
            "m2_construidos": 60, "m2_totales": 65, "habitaciones": 2, "banos": 1,
            "estacionamientos": 1, "precio_mensual": 580000,
        }
        respuesta = self.client.post(reverse("editar_inmueble", args=[inmueble.pk]), datos)
        self.assertRedirects(respuesta, reverse("mis_inmuebles"))
        inmueble.refresh_from_db()
        self.assertEqual(inmueble.precio_mensual, 580000)
        self.assertFalse(inmueble.disponible)
        respuesta = self.client.post(reverse("eliminar_inmueble", args=[inmueble.pk]))
        self.assertRedirects(respuesta, reverse("mis_inmuebles"))
        self.assertFalse(Inmueble.objects.filter(pk=inmueble.pk).exists())

    def test_no_puede_editar_inmueble_ajeno(self):
        self.entrar("jperez")
        ajeno = Inmueble.objects.get(nombre="Depto Las Condes")
        self.assertEqual(self.client.get(reverse("editar_inmueble", args=[ajeno.pk])).status_code, 404)
        self.assertEqual(self.client.post(reverse("eliminar_inmueble", args=[ajeno.pk])).status_code, 404)

    def test_arrendatario_no_puede_editar_inmuebles(self):
        self.entrar("psoto")
        inmueble = Inmueble.objects.first()
        self.assertEqual(self.client.get(reverse("editar_inmueble", args=[inmueble.pk])).status_code, 403)
