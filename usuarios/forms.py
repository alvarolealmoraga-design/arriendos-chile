from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group, User
from django.db import transaction

from inmuebles.models import Perfil

GRUPOS = {
    "arrendador": "Arrendadores",
    "arrendatario": "Arrendatarios",
}


class RegistroForm(UserCreationForm):
    first_name = forms.CharField(label="Nombre", max_length=150)
    last_name = forms.CharField(label="Apellido", max_length=150)
    email = forms.EmailField(label="Correo electrónico")
    rut = forms.CharField(label="RUT", max_length=12, help_text="Ejemplo: 12.345.678-9")
    telefono = forms.CharField(label="Teléfono", max_length=20, required=False)
    tipo_usuario = forms.ChoiceField(label="Tipo de usuario", choices=Perfil.TIPOS_USUARIO)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name", "last_name", "email")

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Ya existe un usuario con este correo.")
        return email

    def clean_rut(self):
        rut = self.cleaned_data["rut"].strip()
        if Perfil.objects.filter(rut=rut).exists():
            raise forms.ValidationError("Ya existe un usuario con este RUT.")
        return rut

    @transaction.atomic
    def save(self, commit=True):
        usuario = super().save(commit=commit)
        if commit:
            tipo = self.cleaned_data["tipo_usuario"]
            Perfil.objects.create(
                usuario=usuario,
                rut=self.cleaned_data["rut"],
                telefono=self.cleaned_data["telefono"],
                tipo_usuario=tipo,
            )
            usuario.groups.add(Group.objects.get(name=GRUPOS[tipo]))
        return usuario


class EditarUsuarioForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")
        labels = {
            "first_name": "Nombre",
            "last_name": "Apellido",
            "email": "Correo electrónico",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for campo in self.fields.values():
            campo.required = True

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Ya existe otro usuario con este correo.")
        return email


class EditarPerfilForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ("telefono", "direccion")
        labels = {
            "telefono": "Teléfono",
            "direccion": "Dirección",
        }
