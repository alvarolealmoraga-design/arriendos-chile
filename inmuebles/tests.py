from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from . import services
from .models import Comuna, Inmueble, Region, TipoInmueble


class CrudInmuebleTest(TestCase):
    def setUp(self):
        call_command("loaddata", "regiones_comunas", "tipos_inmueble", verbosity=0)
        self.comuna = Comuna.objects.get(nombre="Providencia")
        self.dueno = services.crear_usuario(
            "jperez", "Juan", "Pérez", "juan@mail.com", "clave1234",
            rut="11.111.111-1", tipo_usuario="arrendador",
        )

    def crear(self):
        return services.crear_inmueble(
            "Depto Providencia", "Depto luminoso cerca del metro", 60, 65, 1, 2, 1,
            "Av. Providencia 1234", 2, 550000, self.comuna.id, self.dueno.id,
        )

    def test_crear(self):
        inmueble = self.crear()
        self.assertIsNotNone(inmueble.id)
        self.assertEqual(inmueble.comuna.region.nombre, "Región Metropolitana de Santiago")
        self.assertEqual(self.dueno.perfil.tipo_usuario, "arrendador")

    def test_crear_con_comuna_inexistente(self):
        self.assertIsNone(services.crear_inmueble(
            "X", "X", 1, 1, 0, 1, 1, "X", 1, 1, 9999, self.dueno.id))

    def test_listar(self):
        self.crear()
        self.assertEqual(services.listar_inmuebles().count(), 1)
        self.assertEqual(services.listar_inmuebles_por_comuna(self.comuna.id).count(), 1)
        services.imprimir_inmuebles()

    def test_actualizar(self):
        inmueble = self.crear()
        services.actualizar_inmueble(inmueble.id, precio_mensual=600000, disponible=False)
        inmueble.refresh_from_db()
        self.assertEqual(inmueble.precio_mensual, 600000)
        self.assertFalse(inmueble.disponible)

    def test_eliminar(self):
        inmueble = self.crear()
        self.assertTrue(services.eliminar_inmueble(inmueble.id))
        self.assertEqual(Inmueble.objects.count(), 0)
        self.assertFalse(services.eliminar_inmueble(inmueble.id))


class VistasInmueblesTest(TestCase):
    def setUp(self):
        call_command("loaddata", "regiones_comunas", "tipos_inmueble", "usuarios", "inmuebles", verbosity=0)

    def entrar(self, username):
        self.client.login(username=username, password="clave1234")

    def datos_formulario(self, **cambios):
        datos = {
            "nombre": "Casa Ñuñoa Norte", "descripcion": "Casa con jardín", "direccion": "Pedro de Valdivia 3000",
            "tipo_inmueble": TipoInmueble.objects.get(nombre="Casa").id,
            "comuna": Comuna.objects.get(nombre="Ñuñoa").id,
            "m2_construidos": 120, "m2_totales": 200, "habitaciones": 3, "banos": 2,
            "estacionamientos": 2, "precio_mensual": 950000, "disponible": "on",
        }
        datos.update(cambios)
        return datos

    def test_arrendador_ve_formulario_de_nuevo_inmueble(self):
        self.entrar("jperez")
        respuesta = self.client.get(reverse("publicar_inmueble"))
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, "Publicar inmueble")

    def test_crear_inmueble_lo_asigna_al_arrendador(self):
        self.entrar("jperez")
        respuesta = self.client.post(reverse("publicar_inmueble"), self.datos_formulario())
        self.assertRedirects(respuesta, reverse("mis_inmuebles"))
        inmueble = Inmueble.objects.get(nombre="Casa Ñuñoa Norte")
        self.assertEqual(inmueble.propietario.username, "jperez")
        self.assertTrue(inmueble.disponible)

    def test_no_permite_m2_construidos_mayores_que_totales(self):
        self.entrar("jperez")
        respuesta = self.client.post(reverse("publicar_inmueble"), self.datos_formulario(m2_construidos=300))
        self.assertContains(respuesta, "no pueden ser mayores")
        self.assertFalse(Inmueble.objects.filter(nombre="Casa Ñuñoa Norte").exists())

    def test_mis_inmuebles_muestra_solo_los_propios(self):
        self.entrar("jperez")
        respuesta = self.client.get(reverse("mis_inmuebles"))
        self.assertContains(respuesta, "Depto Providencia")
        self.assertNotContains(respuesta, "Depto Las Condes")
        self.assertEqual(len(respuesta.context["inmuebles"]), 7)

    def test_actualizar_inmueble_carga_datos_actuales(self):
        self.entrar("jperez")
        inmueble = Inmueble.objects.get(nombre="Depto Providencia")
        respuesta = self.client.get(reverse("editar_inmueble", args=[inmueble.pk]))
        self.assertContains(respuesta, 'value="Depto Providencia"')

    def test_eliminar_pide_confirmacion(self):
        self.entrar("jperez")
        inmueble = Inmueble.objects.get(nombre="Depto Providencia")
        respuesta = self.client.get(reverse("eliminar_inmueble", args=[inmueble.pk]))
        self.assertContains(respuesta, "¿Seguro que quieres eliminar")
        self.assertTrue(Inmueble.objects.filter(pk=inmueble.pk).exists())

    def test_listado_solo_muestra_disponibles(self):
        self.entrar("psoto")
        respuesta = self.client.get(reverse("listado_inmuebles"))
        self.assertEqual(len(respuesta.context["inmuebles"]), 18)
        self.assertNotContains(respuesta, "Casa Ñuñoa")

    def test_filtros_del_listado(self):
        self.entrar("psoto")
        region_metropolitana = Region.objects.get(nombre="Región Metropolitana de Santiago")
        respuesta = self.client.get(reverse("listado_inmuebles"), {"region": region_metropolitana.id})
        self.assertTrue(all(i.comuna.region_id == region_metropolitana.id for i in respuesta.context["inmuebles"]))
        respuesta = self.client.get(reverse("listado_inmuebles"), {"precio_max": 500000})
        self.assertTrue(all(i.precio_mensual <= 500000 for i in respuesta.context["inmuebles"]))
        respuesta = self.client.get(reverse("listado_inmuebles"), {"tipo": TipoInmueble.objects.get(nombre="Casa").id, "habitaciones_min": 4})
        self.assertEqual([i.nombre for i in respuesta.context["inmuebles"]], ["Casa Puerto Montt"])
        respuesta = self.client.get(reverse("listado_inmuebles"), {"buscar": "playa"})
        self.assertEqual(len(respuesta.context["inmuebles"]), 2)

    def test_detalle_muestra_contacto(self):
        self.entrar("psoto")
        inmueble = Inmueble.objects.get(nombre="Depto Providencia")
        respuesta = self.client.get(reverse("detalle_inmueble", args=[inmueble.pk]))
        self.assertContains(respuesta, "jperez@mail.com")

    def test_detalle_de_inmueble_arrendado_redirige(self):
        self.entrar("psoto")
        arrendado = Inmueble.objects.get(nombre="Casa Ñuñoa")
        self.assertRedirects(self.client.get(reverse("detalle_inmueble", args=[arrendado.pk])), reverse("listado_inmuebles"))
