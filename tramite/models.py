from __future__ import unicode_literals
from django.db import models
from django.utils import timezone
import datetime
from datetime import datetime
from persona.models import *
#from tipos.models import TipoObra



class Tramite(models.Model):
	propietario = models.OneToOneField(Propietario,null=True)
	profesional= models.OneToOneField(Profesional)
	medidas = models.IntegerField()

	#tipo_obra = models.OneToOneField(TipoObra)
	#pago = models.BooleanField(initial=False)
	#colecciones = estados y documentos

	def pago_completo(self):
		this.pago=True

	def save(self):
		if self.pk is None:
			#super save #Iniciado(tramte=self).save()
			return Iniciado(self)
		else:
			print("ya estoyh guardado en la base y esto es un update")
			self.estados.last().__class__.save()

	def get_nombre_estado(self):
		return self.estados.last().fecha, self.estados[-1].__class__.__name__.lower()

	def quien_lo_inspecciono(self):
		agendados = filter(lambda e: isinstance(e, Agendado), self.estados)
		return ", ".join(["%s %s lo inspecciono" % (a.fecha_inspeccion, a.inspector) for a in agendados])

	def hacer(self, accion, *args, **kwargs):
		if hasattr(self.estados[-1], accion):
			metodo = getattr(self.estados[-1], accion)
			self.estados.append(metodo(self, *args, **kwargs))


class Estado(models.Model):
	tramite = models.ForeignKey(Tramite,related_name='estados') # FK related_name=estados
	timestamp = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['-timestamp']


	def agregar_documentacion(self, tramite, documentos):
		tramite.documentos.add(documento)


class Iniciado(Estado):
	def aceptar(self):
		return Aceptado(datetime.now())

		#super save #Iniciado(tramte=self).save()
	def __init__(self, tramite):
		super(Iniciado, self).__init__(tramite)


class Aceptado(Estado):
	def visar(self,tramite, monto, permiso):
		self.agregar_documentacion(tramite,permiso)
		return Visado(datetime.now(), monto,documentos)

	def __init__(self):
		super(Aceptado, self).__init__()


class Visado(Estado):
	monto = models.IntegerField()
	def __init__(self, fecha, monto,documentos):
		super(Visado, self).__init__(fecha)
		self.monto = monto
		self.documentos = documentos

	def revisar(self, fecha, obs = None):
		if obs:
			return Corregido(datetime.now(),obs)
		else:
			return Agendado(datetime.now(),fecha)


class Corregido(Estado):
	def __init__(self,fecha,observacion):
		super(Corregido, self).__init__(fecha)
		observacion=obs

	def revisar(self,fecha,obs = None):
		if obs:
			return Corregido(datetime.now(),obs)
		else:
			return Aceptado(datetime.now())

class Agendado(Estado):

	def __init__(self, fecha): #fecha_inspeccion, inspector
		super(Agendado, self).__init__(fecha)
		self.fecha_inspeccion = None
		self.inspector = None

	def inspeccionar(self, fecha, inspector):
		estado = Agendado(datetime.now())
		estado.fecha_inspeccion = fecha
		estado.inspector= inspector
		return estado

	def realizar_ultima_inspeccion(self,fecha):
		return Inspeccionado(datetime.now(), fecha)


class Inspeccionado(Estado):
	def __init__(self,fecha,fecha_inspeccion):
		super(Inspeccionado, self).__init__(fecha)
		self.fecha_inspeccion = fecha_inspeccion

	def solicitar_final_obra(self):
		if self.tramite.pago:
			return Finalizado(datetime.now())
		else:
			return self

class Finalizado(Estado):
	def __init__(self,fecha):
		super(Finalizado,self).__init__(fecha)
