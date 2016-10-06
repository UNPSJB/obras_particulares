from __future__ import unicode_literals

from django.db import models

class TipoDocumento(models.Model):

    nombre = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=100)
    activo = models.BooleanField()
    fecha_alta = models.DateTimeField()
    fecha_baja = models.DateTimeField()

    def __str__(self):
        return self.nombre


class Documento(models.Model):

    identificador = models.IntegerField()
    tipoDocumento = models.ForeignKey(TipoDocumento)

    def __str__(self):
        return self.tipoDocumento.nombre



class Categoria(models.Model):

    tipo = models.CharField(max_length=2)
    descripcion = models.CharField(max_length=100)

    def __str__(self):
        return "%s -> %s" % (self.tipo, self.descripcion)


class TipoObra(models.Model):

    nombre = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=100)
    categoria = models.ForeignKey(Categoria)

    def __str__(self):
        return self.nombre
