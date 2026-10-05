from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import FiltroInmueblesForm, InmuebleForm
from .models import Inmueble


def inicio(request):
    if request.user.is_authenticated:
        return redirect("perfil")
    return render(request, "inmuebles/inicio.html")


@login_required
@permission_required("inmuebles.view_inmueble", raise_exception=True)
def listar_inmuebles(request):
    inmuebles = (
        Inmueble.objects.filter(disponible=True)
        .select_related("comuna__region", "tipo_inmueble")
        .order_by("comuna__region__id", "comuna__nombre", "precio_mensual")
    )
    filtro = FiltroInmueblesForm(request.GET or None)
    if filtro.is_valid():
        datos = filtro.cleaned_data
        if datos["buscar"]:
            inmuebles = inmuebles.filter(
                Q(nombre__icontains=datos["buscar"])
                | Q(descripcion__icontains=datos["buscar"])
                | Q(direccion__icontains=datos["buscar"])
            )
        if datos["region"]:
            inmuebles = inmuebles.filter(comuna__region=datos["region"])
        if datos["comuna"]:
            inmuebles = inmuebles.filter(comuna=datos["comuna"])
        if datos["tipo"]:
            inmuebles = inmuebles.filter(tipo_inmueble=datos["tipo"])
        if datos["precio_max"] is not None:
            inmuebles = inmuebles.filter(precio_mensual__lte=datos["precio_max"])
        if datos["habitaciones_min"] is not None:
            inmuebles = inmuebles.filter(habitaciones__gte=datos["habitaciones_min"])
    return render(request, "inmuebles/listado.html", {
        "inmuebles": inmuebles,
        "filtro": filtro,
        "total": Inmueble.objects.filter(disponible=True).count(),
    })


@login_required
@permission_required("inmuebles.view_inmueble", raise_exception=True)
def detalle_inmueble(request, pk):
    inmueble = get_object_or_404(
        Inmueble.objects.select_related("comuna__region", "tipo_inmueble", "propietario__perfil"),
        pk=pk,
    )
    if not inmueble.disponible and inmueble.propietario != request.user:
        messages.error(request, "Ese inmueble ya no está disponible para arriendo.")
        return redirect("listado_inmuebles")
    return render(request, "inmuebles/detalle.html", {"inmueble": inmueble})


@login_required
@permission_required("inmuebles.add_inmueble", raise_exception=True)
def mis_inmuebles(request):
    inmuebles = (
        Inmueble.objects.filter(propietario=request.user)
        .select_related("comuna__region", "tipo_inmueble")
        .order_by("-disponible", "nombre")
    )
    return render(request, "inmuebles/mis_inmuebles.html", {"inmuebles": inmuebles})


@login_required
@permission_required("inmuebles.add_inmueble", raise_exception=True)
def crear_inmueble(request):
    if request.method == "POST":
        form = InmuebleForm(request.POST)
        if form.is_valid():
            inmueble = form.save(commit=False)
            inmueble.propietario = request.user
            inmueble.save()
            messages.success(request, f"Inmueble \"{inmueble.nombre}\" publicado correctamente.")
            return redirect("mis_inmuebles")
    else:
        form = InmuebleForm()
    return render(request, "inmuebles/formulario.html", {"form": form, "titulo": "Publicar inmueble", "boton": "Publicar"})


@login_required
@permission_required("inmuebles.change_inmueble", raise_exception=True)
def actualizar_inmueble(request, pk):
    inmueble = get_object_or_404(Inmueble, pk=pk, propietario=request.user)
    if request.method == "POST":
        form = InmuebleForm(request.POST, instance=inmueble)
        if form.is_valid():
            form.save()
            messages.success(request, f"Inmueble \"{inmueble.nombre}\" actualizado correctamente.")
            return redirect("mis_inmuebles")
    else:
        form = InmuebleForm(instance=inmueble)
    return render(request, "inmuebles/formulario.html", {"form": form, "titulo": "Editar inmueble", "boton": "Guardar cambios"})


@login_required
@permission_required("inmuebles.delete_inmueble", raise_exception=True)
def eliminar_inmueble(request, pk):
    inmueble = get_object_or_404(Inmueble, pk=pk, propietario=request.user)
    if request.method == "POST":
        nombre = inmueble.nombre
        inmueble.delete()
        messages.success(request, f"Inmueble \"{nombre}\" eliminado.")
        return redirect("mis_inmuebles")
    return render(request, "inmuebles/eliminar.html", {"inmueble": inmueble})
