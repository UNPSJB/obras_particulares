from __future__ import unicode_literals

from django.db import models

class TipoDocumento(models.Model):

    nombre = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=100)
    activo = models.BooleanField()
    fecha_alta = models.DateTimeField()
    fecha_baja = models.DateTimeField()

    def __str__(self):
        return nombre
