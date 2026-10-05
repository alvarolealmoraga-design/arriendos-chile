from django.urls import path
from django.views.generic import RedirectView

from . import views

urlpatterns = [
    path("registro/", views.registro, name="registro"),
    path("login/", views.IniciarSesionView.as_view(), name="login"),
    path("logout/", views.CerrarSesionView.as_view(), name="logout"),
    path("perfil/", views.perfil, name="perfil"),
    path("perfil/editar/", views.editar_perfil, name="editar_perfil"),
    path("mi-cuenta/", RedirectView.as_view(pattern_name="perfil", permanent=False)),
    path("accounts/login/", RedirectView.as_view(pattern_name="login", query_string=True)),
]
