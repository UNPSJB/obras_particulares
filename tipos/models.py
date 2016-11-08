from __future__ import unicode_literals
import datetime
from django.utils import timezone

from django.db import models


class TipoDocumento(models.Model):
    INICIAR = 1 << 0
    REVISAR = 1 << 1
    CORREGIR = 1 << 2
    VISAR = 1 << 3
    AGENDAR = 1 << 4
    INSPECCIONAR = 1 << 5
    # realizar el pago de un tramite
    PAGAR = 1 << 6
    # Finalizar la obra esto es cuando se pide un final de obra por el ...
    FINALIZAR = 1 << 7
    ACCIONES = [
        (INICIAR, 'Iniciar un tramite'),
        (CORREGIR, 'Corregir un documento durante el tramite'),
        (REVISAR, 'Revisar Correcciones'),
        (VISAR, 'Visar un Tramite'),
        (AGENDAR, 'Agendar nueva fecha de inspeccion'),
        (INSPECCIONAR, 'Registrar una inspeccion'),
        (PAGAR, 'Realizar el pago de un tramite'),
        (FINALIZAR, 'Solicitud de final de obra')
    ]
    nombre = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=100)
    activo = models.BooleanField()
    fecha_alta = models.DateTimeField()
    fecha_baja = models.DateTimeField(blank=True, null=True)
    requerido = models.IntegerField(default=0)

    def __str__(self):
        return self.nombre

    def fue_pubicado_recientemente(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.fecha_alta <= now

    fue_pubicado_recientemente.admin_order_field = 'fecha_alta'
    fue_pubicado_recientemente.boolean = True
    fue_pubicado_recientemente.short_description = 'Publicado recintemente?'

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
