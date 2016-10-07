from __future__ import unicode_literals

from django.db import models


class TipoDocumento(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=100)
    activo = models.BooleanField()
    fecha_alta = models.DateTimeField()
    fecha_baja = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.nombre


class Documento(models.Model):
    identificador = models.IntegerField()
    tipoDocumento = models.ForeignKey(TipoDocumento)

    def __str__(self):
        return self.tipoDocumento.nombre


class TipoObra(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=100)
    categorias = models.CommaSeparatedIntegerField(max_length=100)

    def __str__(self):
        return "%s - %s - Categoria: %s" %(self.nombre, self.descripcion, self.categorias)

    @staticmethod
    def tipos_para_profesional(categorias):
        return TipoObra.objects.filter(categorias__contains=categorias)
