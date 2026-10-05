from django import forms

from .models import Comuna, Inmueble, Region, TipoInmueble


class InmuebleForm(forms.ModelForm):
    class Meta:
        model = Inmueble
        fields = (
            "nombre", "descripcion", "tipo_inmueble", "comuna", "direccion",
            "m2_construidos", "m2_totales", "habitaciones", "banos",
            "estacionamientos", "precio_mensual", "disponible",
        )
        widgets = {"descripcion": forms.Textarea(attrs={"rows": 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["comuna"].queryset = Comuna.objects.select_related("region").order_by("nombre")
        self.fields["tipo_inmueble"].queryset = TipoInmueble.objects.order_by("nombre")

    def clean(self):
        datos = super().clean()
        construidos = datos.get("m2_construidos")
        totales = datos.get("m2_totales")
        if construidos is not None and totales is not None and construidos > totales:
            self.add_error("m2_construidos", "Los m² construidos no pueden ser mayores que los m² totales.")
        return datos


class FiltroInmueblesForm(forms.Form):
    buscar = forms.CharField(label="Buscar", required=False)
    region = forms.ModelChoiceField(label="Región", queryset=Region.objects.none(), required=False, empty_label="Todas")
    comuna = forms.ModelChoiceField(label="Comuna", queryset=Comuna.objects.none(), required=False, empty_label="Todas")
    tipo = forms.ModelChoiceField(label="Tipo", queryset=TipoInmueble.objects.none(), required=False, empty_label="Todos")
    precio_max = forms.IntegerField(label="Precio máximo", required=False, min_value=0)
    habitaciones_min = forms.IntegerField(label="Habitaciones (mín.)", required=False, min_value=0)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        disponibles = Inmueble.objects.filter(disponible=True)
        self.fields["region"].queryset = Region.objects.filter(comunas__inmuebles__in=disponibles).distinct().order_by("id")
        comunas = Comuna.objects.filter(inmuebles__in=disponibles).distinct().order_by("nombre")
        region_id = self.data.get("region")
        if region_id and region_id.isdigit():
            comunas = comunas.filter(region_id=region_id)
        self.fields["comuna"].queryset = comunas
        self.fields["tipo"].queryset = TipoInmueble.objects.filter(inmuebles__in=disponibles).distinct().order_by("nombre")
