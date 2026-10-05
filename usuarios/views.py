from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import Count, Q
from django.shortcuts import redirect, render

from inmuebles.models import Perfil

from .forms import EditarPerfilForm, EditarUsuarioForm, RegistroForm


def registro(request):
    if request.user.is_authenticated:
        return redirect("perfil")
    if request.method == "POST":
        form = RegistroForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            login(request, usuario)
            messages.success(request, f"¡Bienvenido/a {usuario.first_name}! Tu cuenta fue creada correctamente.")
            return redirect("perfil")
    else:
        form = RegistroForm()
    return render(request, "usuarios/registro.html", {"form": form})


class IniciarSesionView(LoginView):
    template_name = "usuarios/login.html"
    redirect_authenticated_user = True

    def form_valid(self, form):
        messages.success(self.request, f"Sesión iniciada como {form.get_user().username}.")
        return super().form_valid(form)


class CerrarSesionView(LogoutView):
    template_name = "usuarios/logout.html"


def obtener_perfil(usuario):
    try:
        return usuario.perfil
    except Perfil.DoesNotExist:
        return None


@login_required
def perfil(request):
    perfil_usuario = obtener_perfil(request.user)
    resumen = None
    if perfil_usuario and perfil_usuario.tipo_usuario == "arrendador":
        resumen = request.user.inmuebles.aggregate(
            total=Count("id"),
            disponibles=Count("id", filter=Q(disponible=True)),
            arrendados=Count("id", filter=Q(disponible=False)),
        )
    permisos = sorted(p for p in request.user.get_all_permissions() if p.startswith("inmuebles."))
    return render(request, "usuarios/perfil.html", {
        "perfil": perfil_usuario,
        "resumen": resumen,
        "permisos": permisos,
    })


@login_required
def editar_perfil(request):
    perfil_usuario = obtener_perfil(request.user)
    if request.method == "POST":
        form_usuario = EditarUsuarioForm(request.POST, instance=request.user)
        form_perfil = EditarPerfilForm(request.POST, instance=perfil_usuario) if perfil_usuario else None
        if form_usuario.is_valid() and (form_perfil is None or form_perfil.is_valid()):
            form_usuario.save()
            if form_perfil:
                form_perfil.save()
            messages.success(request, "Tus datos fueron actualizados correctamente.")
            return redirect("perfil")
    else:
        form_usuario = EditarUsuarioForm(instance=request.user)
        form_perfil = EditarPerfilForm(instance=perfil_usuario) if perfil_usuario else None
    return render(request, "usuarios/editar_perfil.html", {
        "formularios": [f for f in (form_usuario, form_perfil) if f],
        "perfil": perfil_usuario,
    })
