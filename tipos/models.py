from __future__ import unicode_literals
import datetime
from django.utils import timezone
from django.db import models
from persona.models import *


class TipoDocumento(models.Model):
    INICIAR = 1 << 0
    VISAR = 1 << 2
    APROBAR_INSPECCION = 1 << 3
    APROBAR_TRAMITE = 1 << 4
    SOLICITAR_NO_APROBAR_TRAMITE = 1 << 5
    NO_APROBAR_TRAMITE = 1 << 6
    SOLICITAR_APROBAR_TRAMITE_PROPIETARIO = 1 << 7
    SOLICITAR_FINAL_OBRA_TOTAL = 1 << 8
    SOLICITAR_NO_FINAL_OBRA_TOTAL = 1 << 9
    FINALIZAR = 1 << 10
    NO_FINALIZAR = 1 << 11
    SOLICITAR_FINAL_OBRA_TOTAL_PROPIETARIO = 1 << 12
    PAGAR = 1 << 13
    INGRESAR_CORRECCIONES = 1 << 14
    ACCIONES = [
        (INICIAR, "Profesional - Iniciar tramite"),
        (VISAR, "Visador - Visar tramite"),
        (APROBAR_INSPECCION, "Inspector / JefeInspector - Inspeccionar tramite"),
        (APROBAR_TRAMITE, "Administrativo - Aprobar tramite"),
        (SOLICITAR_NO_APROBAR_TRAMITE, "Profesional - Solicitar no aprobar tramite"),
        (NO_APROBAR_TRAMITE, "Administrativo - No aprobar tramite"),
        (SOLICITAR_APROBAR_TRAMITE_PROPIETARIO, "Propietario - Solicitar aprobar tramite"),
        (SOLICITAR_FINAL_OBRA_TOTAL, "Profesional - Solicitar final obra total de tramite"),
        (SOLICITAR_NO_FINAL_OBRA_TOTAL, "Profesional - Solicitar no final obra total de tramite"),
        (FINALIZAR, "Administrativo - Finalizar tramite"),
        (NO_FINALIZAR, "Administrativo - No finalizar tramite"),
        (SOLICITAR_FINAL_OBRA_TOTAL_PROPIETARIO, "Propietario - Solicitar final obra total de tramite"),
        (PAGAR, "Administrativo - Pagar tramite"),
        (INGRESAR_CORRECCIONES, "Profesional - Cargar correcciones del tramite")
    ]
    nombre = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=100)
    activo = models.BooleanField(default=True)
    fecha_alta = models.DateField()
    fecha_baja = models.DateField(blank=True, null=True)
    requerido = models.IntegerField(default=0)

    def __str__(self):
        return "{} - {} - Requerido para {}".format(self.nombre, self.descripcion, self.requerido_para())

    """
    Metodo que se encarga de obtener los tipos de documentos que son necesarios para tal accion de cambio de estado.
    """

    @staticmethod
    def get_tipos_documentos_para_momento(accion):
        devolucion = []
        for tipo in TipoDocumento.objects.filter(activo=True): #Se filtran los tipos de documentos que estan activos.
            if (tipo.requerido & accion) == accion:
                devolucion.append(tipo)
        return devolucion

    """
    Metodo que se encarga de devolver la accion para la que se lo requiere al tramite
    """

    def requerido_para(self):
        match = [accion for accion in TipoDocumento.ACCIONES if accion[0] == self.requerido]
        return match[0][1].split(" - ")[1]
        
    """
    Metodo que se encarga de devolver la persona que utiliza el tipo de documento en el
    sistema
    """

    def quien_lo_utiliza(self):
        match = [accion for accion in TipoDocumento.ACCIONES if accion[0] == self.requerido]
        return match[0][1].split(" - ")[0]


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
