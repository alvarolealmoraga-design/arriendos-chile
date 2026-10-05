from django.urls import path

from . import views

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("inmuebles/", views.listar_inmuebles, name="listado_inmuebles"),
    path("inmuebles/<int:pk>/", views.detalle_inmueble, name="detalle_inmueble"),
    path("inmuebles/mis-inmuebles/", views.mis_inmuebles, name="mis_inmuebles"),
    path("inmuebles/nuevo/", views.crear_inmueble, name="publicar_inmueble"),
    path("inmuebles/<int:pk>/editar/", views.actualizar_inmueble, name="editar_inmueble"),
    path("inmuebles/<int:pk>/eliminar/", views.eliminar_inmueble, name="eliminar_inmueble"),
]
