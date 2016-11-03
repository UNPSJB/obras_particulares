from __future__ import unicode_literals
from django.db import models
from django.utils import timezone
import datetime
from persona.models import *
from tipos.models import *


class Estado(models.Model):
	fecha = models.DateTimeField(blank=True, null=True)
	

class Tramite(models.Model):
    propietario = models.OneToOneField(Propietario,null=True)
    profesional= models.OneToOneField(Profesional)
    medidas = models.IntegerField()
    tipoObra = models.OneToOneField(TipoObra)
    estados = models.ForeignKey(Estado)

    def get_nombre_estado(self):
        return self.estados[-1].fecha, self.estados[-1].__class__.__name__.lower()

    def quien_lo_inspecciono(self):
        agendados = filter(lambda e: isinstance(e, Agendado), self.estados)
        return ", ".join(["%s %s lo inspecciono" % (a.fecha_inspeccion, a.inspector) for a in agendados])
  

class Iniciado(Estado):
	def revisar(self, tramite, obs = None):
		if obs:
			return Corregido(datetime.now())
		else:
			return Aceptado(datetime.now())

class Aceptado(Estado):
	def visar(self, tramite, monto, documentos):
		tramite.documentos = tramite.documentos + documentos
		return Visado(datetime.now(), monto)


class Visado(Estado):
	monto = models.IntegerField()

	def agendar(self, tramite, fecha, inspector):
		return Agendado(datetime.now(), fecha, inspector)


class Agendado(Estado):
	fecha_inspeccion = models.DateTimeField(blank=True, null=True)
	
	def agendar(self, tramite, fecha, inspector):
		return Agendado(datetime.now(), fecha, inspector)

class Corregido(Estado):
	pass