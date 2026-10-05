from django.contrib.auth.models import User

from .models import Comuna, Inmueble, Perfil, TipoInmueble


def crear_usuario(username, first_name, last_name, email, password, rut,
                  tipo_usuario="arrendatario", direccion="", telefono=""):
    try:
        usuario = User.objects.create_user(
            username=username, first_name=first_name, last_name=last_name,
            email=email, password=password,
        )
        Perfil.objects.create(
            usuario=usuario, rut=rut, tipo_usuario=tipo_usuario,
            direccion=direccion, telefono=telefono,
        )
        return usuario
    except Exception as e:
        print(f"Error al crear el usuario: {e}")
        return None


def crear_inmueble(nombre, descripcion, m2_construidos, m2_totales, estacionamientos,
                   habitaciones, banos, direccion, tipo_inmueble_id, precio_mensual,
                   comuna_id, propietario_id):
    try:
        comuna = Comuna.objects.get(id=comuna_id)
        tipo_inmueble = TipoInmueble.objects.get(id=tipo_inmueble_id)
        propietario = User.objects.get(id=propietario_id)
        inmueble = Inmueble(
            nombre=nombre, descripcion=descripcion,
            m2_construidos=m2_construidos, m2_totales=m2_totales,
            estacionamientos=estacionamientos, habitaciones=habitaciones, banos=banos,
            direccion=direccion, tipo_inmueble=tipo_inmueble,
            precio_mensual=precio_mensual, comuna=comuna, propietario=propietario,
        )
        inmueble.save()
        return inmueble
    except Comuna.DoesNotExist:
        print(f"Error: no existe la comuna con id {comuna_id}")
    except TipoInmueble.DoesNotExist:
        print(f"Error: no existe el tipo de inmueble con id {tipo_inmueble_id}")
    except User.DoesNotExist:
        print(f"Error: no existe el usuario con id {propietario_id}")
    except Exception as e:
        print(f"Error al guardar el inmueble: {e}")
    return None


def listar_inmuebles():
    return Inmueble.objects.select_related("comuna", "tipo_inmueble", "propietario").order_by("id")


def listar_inmuebles_por_comuna(comuna_id):
    return Inmueble.objects.filter(comuna_id=comuna_id).order_by("id")


def obtener_inmueble(inmueble_id):
    try:
        return Inmueble.objects.get(id=inmueble_id)
    except Inmueble.DoesNotExist:
        print(f"Error: no existe el inmueble con id {inmueble_id}")
        return None


def imprimir_inmuebles(inmuebles=None):
    if inmuebles is None:
        inmuebles = listar_inmuebles()
    if not inmuebles:
        print("No hay inmuebles registrados.")
    for i in inmuebles:
        estado = "disponible" if i.disponible else "arrendado"
        print(f"[{i.id}] {i.nombre} | {i.tipo_inmueble.nombre} | "
              f"{i.comuna.nombre} | ${i.precio_mensual:,.0f} | {estado}".replace(",", "."))


def actualizar_inmueble(inmueble_id, **campos):
    inmueble = obtener_inmueble(inmueble_id)
    if inmueble is None:
        return None
    try:
        for campo, valor in campos.items():
            setattr(inmueble, campo, valor)
        inmueble.save()
        return inmueble
    except Exception as e:
        print(f"Error al actualizar el inmueble: {e}")
        return None


def eliminar_inmueble(inmueble_id):
    inmueble = obtener_inmueble(inmueble_id)
    if inmueble is None:
        return False
    inmueble.delete()
    return True
