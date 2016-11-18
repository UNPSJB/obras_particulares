from __future__ import unicode_literals
from django.db import models
from django.utils import timezone
import datetime
from persona.models import *
from tipos.models import *


class Tramite(models.Model):
    propietario = models.ForeignKey(Propietario,blank=True, null=True,unique=False)
    profesional= models.ForeignKey(Profesional,unique=False)
    medidas = models.IntegerField()
    tipo_obra = models.ForeignKey(TipoObra)
    domicilio = models.CharField(max_length=50,blank=True)
    #pago = models.BooleanField(initial=False)
    
    def save(self):
        if self.pk is None:
            super(Tramite, self).save(force_insert=True)
            i = Iniciado(tramite=self)
            i.save()
            return self
        else:
            return super(Tramite, self).save(force_update=True)

    def estado_actual(self):
        return self.estados.last().__class__.__name__.lower()

    def quien_lo_inspecciono(self):
        agendados = filter(lambda e: isinstance(e, Agendado), self.estados)
        return ", ".join(["%s %s lo inspecciono" % (a.fecha_inspeccion, a.inspector) for a in agendados])

    def hacer(self, accion, *args, **kwargs):
        if hasattr(self.estados[-1], accion):
            metodo = getattr(self.estados[-1], accion)
            self.estados.append(metodo(self, *args, **kwargs))


class Estado(models.Model):
    tramite = models.ForeignKey(Tramite, related_name='estados')  # FK related_name=estados
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-timestamp']

    def agregar_documentacion(self, tramite, documentos):
        self.documentos.add(documento)  # buscar tramite con fk y asignarle documentos



class Iniciado(Estado):
    CADENA_DEFAULT = "En este momento no se poseen observaciones sobre el tramite"
    observacion = models.CharField(max_length=100, default=CADENA_DEFAULT)

    def aceptar(self):
        return Aceptado(tramite=self.tramite)

    def rechazar(self, observaciones):
        estado = Iniciado(tramite=self.tramite)
        estado.observacion = observaciones
        return estado

    def __str__(self):
        return "iniciado"



class Aceptado(Estado):
    def visar(self, monto, permiso):
        return Visado(self, monto=monto, documentos=permiso)

    def __init__(self, tramite):
        super(Aceptado, self).__init__(tramite)


class Visado(Estado):
    monto = models.FloatField()
    permiso = models.CharField(max_length=20)

    def __init__(self, tramite, monto, documentos):
        super(Visado, self).__init__(tramite)
        self.monto = monto
        self.agregar_documentacion(documentos)

    def corregir_visado(self, observacion):
        return Corregido(tramite=self.tramite, observaciones=observacion)

    def agendar(self, fecha_inspeccion):
        return Agendado(tramite=self.tramite, fecha=fech)


class Corregido(Estado):
    CADENA_DEFAULT = "En este momento no se poseen observaciones sobre el tramite"
    observacion = models.CharField(max_length=100, default=CADENA_DEFAULT)

    def __init__(self, tramite, observaciones):
        super(Corregido, self).__init__(tramite)
        self.observacion = observaciones

    def corregir(self, documentos, aclaraciones):  # realiza el profesional, self.observaciones ==aclaraciones
        estado = Corregido(tramite=self.tramite, observaciones=aclaraciones)
        estado.agregar_documentacion(documentos=documentos)
        return estado

    def aceptar(self):
        return Aceptado(tramite=self.tramite)


class Agendado(Estado):
    def __init__(self, tramite, fecha_inspeccion):  # inspector
        super(Agendado, self).__init__(tramite)
        self.fecha_inspeccion = fecha_inspeccion
        self.inspector = None

    def inspeccionar(self, fecha_inspeccion, inspector):
        estado = Agendado(datetime.now())
        estado.fecha_inspeccion = fecha_inspeccion
        estado.inspector = inspector
        return estado

    def asignar_fecha_inspeccion(self, fecha):
        self.fecha_inspeccion = fecha

    def asignar_inspector(self, inspector):
        self.inspector = inspector

    def realizar_ultima_inspeccion(self, fecha):
        self.fecha_inspeccion_final = fecha

    def inspeccionar_final(self):
        if datetime.datetime.now() > self.fecha_inspeccion_final:
            return Inspeccionado(tramite=self.tramite)  # ver si tiene al menos 3 inspecciones--consulta bd

    def corregir_errores_obra(self, observacion):
        return Corregido(tramite=self.tramite, observaciones=observacion)


class Inspeccionado(Estado):
    def __init__(self, tramite):  # fecha_inspeccion
        super(Inspeccionado, self).__init__(tramite)

    def solicitar_final_obra(self):  # fecha_inspeccion_final en la solucitud?
        if self.tramite.pago_completo:  # Tramite.objects.get(pk=tramite.pk).pago_completo
            return Finalizado(self.tramite)
        else:
            return self


class Finalizado(Estado):
    def __init__(self, tramite):
        super(Finalizado, self).__init__(tramite)
