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


    # recibe una accion "visar", "iniciar", etc y devuelve una lista de tipos para esa accion particular
    @staticmethod
    def get_tipos_documentos_para_momento(momento):
        argumentos = ["INICIAR", "REVISAR", "CORREGIR", "VISAR", "AGENDAR", "INSPECCIONAR", "PAGAR", "FINALIZAR"]
        tipos = TipoDocumento.objects.all()
        devolucion = []
        for indice in xrange(len(argumentos)):
            if (momento == argumentos[indice]):
                valor = 1 << indice
        for tipo in tipos:
            if ((tipo.requerido & valor) == valor):
                devolucion.append(tipo)
        return devolucion





class TipoObra(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.CharField(max_length=100)
    categorias = models.CharField(max_length=100, blank= True, null = True)

    def __str__(self):
        return "%s - %s - Categoria: %s" %(self.nombre, self.descripcion, self.categorias)

    @staticmethod
    def tipos_para_profesional(categorias):
        return TipoObra.objects.filter(categorias__contains=categorias)
