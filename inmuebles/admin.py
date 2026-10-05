from django.contrib import admin

from .models import Comuna, Inmueble, Perfil, Region, TipoInmueble

admin.site.site_header = "Administración Arriendos"
admin.site.site_title = "Arriendos Admin"
admin.site.index_title = "Gestión de inmuebles, regiones y comunas"


class RegionAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "cantidad_comunas")
    search_fields = ("nombre",)
    list_filter = ("nombre",)
    ordering = ("id",)

    @admin.display(description="Comunas")
    def cantidad_comunas(self, obj):
        return obj.comunas.count()


class ComunaAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "region")
    search_fields = ("nombre", "region__nombre")
    list_filter = ("region",)
    ordering = ("id",)


class TipoInmuebleAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "descripcion")
    search_fields = ("nombre",)
    ordering = ("id",)


class InmuebleAdmin(admin.ModelAdmin):
    list_display = (
        "id", "nombre", "tipo_inmueble", "comuna_nombre", "region",
        "habitaciones", "banos", "precio_mensual", "disponible", "propietario",
    )
    search_fields = ("nombre", "descripcion", "direccion", "comuna__nombre", "comuna__region__nombre")
    list_filter = ("tipo_inmueble", "disponible", "comuna__region", "comuna", "habitaciones")
    list_editable = ("disponible",)
    list_per_page = 20
    ordering = ("id",)

    @admin.display(description="Comuna", ordering="comuna__nombre")
    def comuna_nombre(self, obj):
        return obj.comuna.nombre

    @admin.display(description="Región", ordering="comuna__region__nombre")
    def region(self, obj):
        return obj.comuna.region.nombre


class PerfilAdmin(admin.ModelAdmin):
    list_display = ("id", "usuario", "rut", "tipo_usuario", "telefono")
    search_fields = ("usuario__username", "usuario__first_name", "usuario__last_name", "rut")
    list_filter = ("tipo_usuario",)


admin.site.register(Region, RegionAdmin)
admin.site.register(Comuna, ComunaAdmin)
admin.site.register(TipoInmueble, TipoInmuebleAdmin)
admin.site.register(Inmueble, InmuebleAdmin)
admin.site.register(Perfil, PerfilAdmin)
