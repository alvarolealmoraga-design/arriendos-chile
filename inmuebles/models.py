from django.contrib.auth.models import User
from django.db import models


class Region(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = "región"
        verbose_name_plural = "regiones"

    def __str__(self):
        return self.nombre


class Comuna(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    region = models.ForeignKey(Region, on_delete=models.PROTECT, related_name="comunas", verbose_name="región")

    def __str__(self):
        return f"{self.nombre} ({self.region.nombre})"


class Perfil(models.Model):
    TIPOS_USUARIO = [
        ("arrendatario", "Arrendatario"),
        ("arrendador", "Arrendador"),
    ]
    id = models.AutoField(primary_key=True)
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name="perfil")
    tipo_usuario = models.CharField(max_length=20, choices=TIPOS_USUARIO, default="arrendatario", verbose_name="tipo de usuario")
    rut = models.CharField(max_length=12, unique=True, verbose_name="RUT")
    direccion = models.CharField(max_length=200, blank=True)
    telefono = models.CharField(max_length=20, blank=True, verbose_name="teléfono")

    class Meta:
        verbose_name_plural = "perfiles"

    def __str__(self):
        return f"{self.usuario.get_full_name() or self.usuario.username} ({self.tipo_usuario})"


class TipoInmueble(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.CharField(max_length=200, blank=True, verbose_name="descripción")

    class Meta:
        verbose_name = "tipo de inmueble"
        verbose_name_plural = "tipos de inmueble"

    def __str__(self):
        return self.nombre


class Inmueble(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(verbose_name="descripción")
    m2_construidos = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="m² construidos")
    m2_totales = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="m² totales")
    estacionamientos = models.PositiveIntegerField(default=0)
    habitaciones = models.PositiveIntegerField(default=1)
    banos = models.PositiveIntegerField(default=1, verbose_name="baños")
    direccion = models.CharField(max_length=200, verbose_name="dirección")
    tipo_inmueble = models.ForeignKey(TipoInmueble, on_delete=models.PROTECT, related_name="inmuebles", verbose_name="tipo de inmueble")
    precio_mensual = models.DecimalField(max_digits=10, decimal_places=0, verbose_name="precio mensual")
    disponible = models.BooleanField(default=True)
    comuna = models.ForeignKey(Comuna, on_delete=models.PROTECT, related_name="inmuebles")
    propietario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="inmuebles")

    def __str__(self):
        return f"[{self.id}] {self.nombre} - {self.comuna.nombre} - ${self.precio_mensual}"
