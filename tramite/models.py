from __future__ import unicode_literals
from django.db import models
from django.utils import timezone
import datetime
from persona.models import *
from tipos.models import *


class Estado(models.Model):
    fecha = models.DateTimeField(blank=False)

    def __init__(self, fecha_creacion):
        self.fecha = fecha_creacion

class Tramite(models.Model):
    propietario = models.OneToOneField(Propietario, null=True)
    #profesional = models.OneToOneField(Profesional)
    medidas = models.IntegerField()
    tipoObra = models.OneToOneField(TipoObra)
    #estados = models.ForeignKey(Estado)

    def get_nombre_estado(self):
        return self.estados[-1].fecha, self.estados[-1].__class__.__name__.lower()

    def quien_lo_inspecciono(self):
        agendados = filter(lambda e: isinstance(e, Agendado), self.estados)
        return ", ".join(["%s %s lo inspecciono" % (a.fecha_inspeccion, a.inspector) for a in agendados])


class Iniciado(Estado):
    def revisar(self, tramite, obs=None):
        if obs:
            return Iniciado(datetime.now())
        else:
            return Aceptado(datetime.now())

    def __init__(self, fecha):
        super(Iniciado, self).__init__(fecha)

class Aceptado(Estado):
    def visar(self, monto, documentos):
        tramite.documentos = tramite.documentos + documentos
        return Visado(datetime.now(), monto, documentos)

    def __init__(self, fecha):
        super(Aceptado, self).__init__(fecha)

class Visado(Estado):
    monto = models.IntegerField()

    def __init__(self, fecha, monto, documentos):
        super(Visado, self).__init__(fecha)
        self.monto = monto
        self.documentos = documentos

    def revisar(self, fecha, obs=None):
        if obs:
            return Corregido(datetime.now(), obs)
        else:
            return Agendado(datetime.now())


class Corregido(Estado):
    def __init__(self, fecha, observacion):
        super(Corregido, self).__init__(fecha)
        observacion = obs

    def revisar(self, fecha, obs=None):
        if obs:
            return Corregido(datetime.now(), obs)
        else:
            return Aceptado(datetime.now())

class Agendado(Estado):
    def __init__(self, fecha, fecha_inspeccion, inspector):
        super(Agendado, self).__init__(fecha)
        self.fecha_inspeccion = fecha_inspeccion
        self.inspector = inspector

        def inspeccionar(self, fecha, inspector):
            return Agendado(datetime.now(), fecha, inspector)

        def realizar_ultima_inspeccion(self, fecha):
            return Inspeccionado(datetime.now(), fecha)


class Inspeccionado(Estado):
    def __init__(self, fecha, fecha_inspeccion):
        super(Inspeccionado, self).__init__(fecha)
        self.fecha_inspeccion = fecha_inspeccion

    def solicitar_final_obra(self):
        return Finalizado(datetime.now())


class Finalizado(Estado):
    def __init__(self, fecha):
        super(Finalizado, self).__init__(fecha)
