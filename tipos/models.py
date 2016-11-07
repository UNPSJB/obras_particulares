from __future__ import unicode_literals
import datetime
from django.utils import timezone

from django.db import models


class TipoDocumento(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=100)
    activo = models.BooleanField()
    fecha_alta = models.DateTimeField()
    fecha_baja = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.nombre

    def fue_pubicado_recientemente(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.fecha_alta <= now

    fue_pubicado_recientemente.admin_order_field = 'fecha_alta'
    fue_pubicado_recientemente.boolean = True
    fue_pubicado_recientemente.short_description = 'Publicado recintemente?'


class Documento(models.Model):
    identificador = models.IntegerField(unique=True)
    tipo_documento = models.ForeignKey(TipoDocumento)

    def __str__(self):
        return self.tipo_documento.nombre


class TipoObra(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.CharField(max_length=100)
    categorias = models.CharField(max_length=100, blank= True, null = True)

    def __str__(self):
        return "%s - %s - Categoria: %s" %(self.nombre, self.descripcion, self.categorias)

    @staticmethod
    def tipos_para_profesional(categorias):
        return TipoObra.objects.filter(categorias__contains=categorias)
