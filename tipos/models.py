from __future__ import unicode_literals
import datetime
from django.utils import timezone
from django.db import models
from persona.models import *


class TipoDocumento(models.Model):
    INICIAR = 1 << 0
    #REVISAR = 1 << 1
    #ACEPTAR = 1 << 0
    #RECHAZAR = 1 << 0
    #AGENDAR_VISADO = 1 << 0
    VISAR = 1 << 2
    CORREGIR = 1 << 3
    #AGENDAR_INSPECCION = 1 << 0
    APROBAR_INSPECCION = 1 << 4
    #SOLICITAR_APROBAR_TRAMITE = 1 << 0
    APROBAR_TRAMITE = 1 << 5
    SOLICITAR_NO_APROBAR_TRAMITE = 1 << 6


    NO_APROBAR_TRAMITE = 1 << 7
    SOLICITAR_APROBAR_TRAMITE_PROPIETARIO = 1 << 8
    SOLICITAR_FINAL_OBRA_TOTAL = 1 << 9
    SOLICITAR_NO_FINAL_OBRA_TOTAL = 1 << 10
    FINALIZAR = 1 << 11
    NO_FINALIZAR = 1 << 12
    SOLICITAR_FINAL_OBRA_TOTAL_PROPIETARIO = 1 << 13
    #SOLICITAR_FINAL_OBRA_PARCIAL = 1 << 0
    PAGAR = 1 << 14
    #DAR_DE_BAJA = 1 << 0

    ACCIONES = [
        (INICIAR, "Iniciar tramite"),
        #(REVISAR, "Revisar tramite"),
        #(ACEPTAR, "Aceptar tramite"),
        #(RECHAZAR, "Rechazar tramite"),
        #(AGENDAR_VISADO, "Agendar tramite para visado"),
        (VISAR, "Visar tramite"),
        (CORREGIR, "Corregir tramite"),
        #(AGENDAR_INSPECCION, "Agendar tramite para inspeccion"),
        (APROBAR_INSPECCION, "Inspeccionar tramite"),
        #(SOLICITAR_APROBAR_TRAMITE, "Solicitar aprobar tramite"),
        (APROBAR_TRAMITE, "Aprobar tramite"),
        (SOLICITAR_NO_APROBAR_TRAMITE, "Solicitar no aprobar tramite"),
        (NO_APROBAR_TRAMITE, "No aprobar tramite"),
        (SOLICITAR_APROBAR_TRAMITE_PROPIETARIO, "Propietario solicita aprobar tramite"),
        (SOLICITAR_FINAL_OBRA_TOTAL, "Solicitar final obra total de tramite"),
        (SOLICITAR_NO_FINAL_OBRA_TOTAL, "Solicitar no final obra total de tramite"),
        (FINALIZAR, "Finalizar tramite"),
        (NO_FINALIZAR, "No finalizar tramite"),
        (SOLICITAR_FINAL_OBRA_TOTAL_PROPIETARIO, "Propietario solicita final obra total de tramite"),
        #(SOLICITAR_FINAL_OBRA_PARCIAL, "Solicitar final obra parcial de tramite"),
        (PAGAR, "Pagar tramite")
        #(DAR_DE_BAJA, "Dar_de_baja tramite")
    ]
    nombre = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=100)
    activo = models.BooleanField(default=True)
    fecha_alta = models.DateField()
    fecha_baja = models.DateField(blank=True, null=True)
    requerido = models.IntegerField(default=0)

    def __str__(self):
        return "{}, {}".format(self.nombre, self.descripcion)

    @staticmethod
    def get_tipos_documentos_para_momento(accion):
        devolucion = []
        for tipo in TipoDocumento.objects.all():
            if (tipo.requerido & accion) == accion:
                devolucion.append(tipo)
        return devolucion


class TipoObra(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.CharField(max_length=100)
    categorias = models.IntegerField(choices=Profesional.CATEGORIAS, default=1)
    valor_de_superficie = models.IntegerField(default=15)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

    @staticmethod
    def tipos_para_profesional(categorias):
        return TipoObra.objects.filter(categorias__contains=categorias)
