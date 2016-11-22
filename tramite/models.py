from __future__ import unicode_literals
from django.db import models
from django.utils import timezone
import datetime
from persona.models import *
from tipos.models import *

from openpyxl import load_workbook
"""from django_excel import *
import pyexcel as pe"""
from os.path import basename
import csv
from decimal import Decimal


class TramiteBaseManager(models.Manager):
    pass

class TramiteQuerySet(models.QuerySet):
    def ultimo_estado(self):
        return self.annotate(max_date=models.Max('estados__timestamp')).filter(estados__timestamp=models.F('max_date'))

    def en_estado(self, estados):
        if type(estados) != list:
            estados = [estados]
        return self.ultimo_estado().filter(estados__tipo__in=[ e.TIPO for e in estados])

TramiteManager = TramiteBaseManager.from_queryset(TramiteQuerySet)


class Tramite(models.Model):
    INICIAR = "iniciar"
    REVISAR = "revisar"
    CORREGIR = "corregir"
    ACEPTAR = "aceptar"
    RECHAZAR = "rechazar"
    VISAR = "visar"
    AGENDAR = "agendar"
    INSPECCIONAR = "inspeccionar"
    # realizar el pago de un tramite
    PAGAR = "pagar"
    # Finalizar la obra esto es cuando se pide un final de obra por el ...
    FINALIZAR = "finalizar"
    propietario = models.ForeignKey(Propietario,blank=True, null=True,unique=False)
    profesional= models.ForeignKey(Profesional,unique=False)
    medidas = models.IntegerField()
    tipo_obra = models.ForeignKey(TipoObra)
    domicilio = models.CharField(max_length=50,blank=True)
    monto_a_pagar = models.DecimalField(max_digits=10, decimal_places=2)
    monto_pagado = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return   "Numero de tramite: {} - Profesional: {} - Propietario: {}" .format(self.pk, self.profesional, self.propietario)

@classmethod
def new(cls, usuario, propietario, profesional, tipo_obra, medidas, documentos):
    if any(map(lambda d: d.tipo_documento != TipoDocumento.INICIAR, documentos)):
        raise Exception("Un documento no es de tipo iniciar")
    t = cls(propietario=propietario, profesional=profesional, medidas=medidas, tipo_obra=tipo_obra)
    t.save()
    for doc in documentos:
        doc.tramite = t
        doc.save()
    t.hacer(Tramite.INICIAR, usuario, observacion="Arranca el tramite")
    return t

    def estado(self):
        if self.estados.exists():
            return self.estados.latest().related()

    def quien_lo_inspecciono(self):
        agendados = filter(lambda e: isinstance(e, Agendado), self.estados)
        return ", ".join(["%s %s lo inspecciono" % (a.fecha_inspeccion, a.inspector) for a in agendados])

    def hacer(self, accion, usuario=None, *args, **kwargs):
        estado_actual = self.estado()
        if estado_actual is not None and hasattr(estado_actual, accion):
            metodo = getattr(estado_actual, accion)
            estado_nuevo = metodo(self, *args, **kwargs)
            if estado_actual is not None:
                estado_nuevo.usuario = usuario
                estado_nuevo.save()
        elif estado_actual is None:
            Iniciado(tramite=self, usuario=usuario, *args, **kwargs).save()


class Estado(models.Model):
    TIPO = 0
    TIPOS = [
        (0, "Estado")
    ]
    tramite = models.ForeignKey(Tramite, related_name='estados')  # FK related_name=estados
    tipo = models.PositiveSmallIntegerField(choices=TIPOS)
    usuario = models.ForeignKey(Usuario)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        get_latest_by = 'timestamp'

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.tipo = self.__class__.TIPO
        super(Estado, self).save(*args, **kwargs)

    def agregar_documentacion(self, tramite, documentos):
        self.tramite.documentos.add(documento)  # buscar tramite con fk y asignarle documentos

    def related(self):
        return self.__class__ != Estado and self or getattr(self, self.get_tipo_display())

    @classmethod
    def register(cls, klass):
        cls.TIPOS.append((klass.TIPO, klass.__name__.lower()))


class Iniciado(Estado):
    TIPO = 1
    CADENA_DEFAULT = "En este momento no se poseen observaciones sobre el tramite"
    observacion = models.CharField(max_length=100, default=CADENA_DEFAULT)

    def aceptar(self, tramite):
        return Aceptado(tramite=tramite)

    def rechazar(self, tramite, observacion):
        return Iniciado(tramite=tramite, observacion=observacion)

    def __str__(self):
        return "iniciado"



class Aceptado(Estado):
    TIPO = 2
    def visar(self, tramite, monto, permiso):
        return Visado(tramite=tramite, monto=monto, permiso=permiso)


class Visado(Estado):
    TIPO = 3
    monto = models.FloatField()
    permiso = models.CharField(max_length=20)

    def corregir(self, tramite, observacion):
        return Corregido(tramite=tramite, observaciones=observacion)

    def agendar(self, tramite, fecha_inspeccion, inspector=None):
        return Agendado(tramite=tramite, fecha=fecha_inspeccion, inspector=None)


class Corregido(Estado):
    TIPO = 4
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
    TIPO = 5
    inspector = models.ForeignKey(Usuario, null=True, blank=True)
    fecha = models.DateTimeField(auto_now=True)

    def inspeccionar(self, tramite, fecha_inspeccion, inspector=None):
        if inspector is not None and self.inspector is None:
            self.inspector = inspector
            self.save()
        return Agendado(tramite=tramite, fecha=fecha_inspeccion, inspector=None)

    def asignar_fecha_inspeccion(self, fecha):
        self.fecha_inspeccion = fecha

    def asignar_inspector(self, inspector):
        self.inspector = inspector

    def realizar_ultima_inspeccion(self, fecha):
        self.fecha_inspeccion_final = fecha

    def inspeccionar_final(self):
        if datetime.datetime.now() > self.fecha_inspeccion_final:
            return Inspeccionado(tramite=self.tramite)  # ver si tiene al menos 3 inspecciones--consulta bd

    def corregir(self, tramite, observacion):
        return Corregido(tramite=tramite, observaciones=observacion)


class Inspeccionado(Estado):
    TIPO = 6
    def __init__(self, tramite):  # fecha_inspeccion
        super(Inspeccionado, self).__init__(tramite)

    def solicitar_final_obra(self):  # fecha_inspeccion_final en la solucitud?
        if self.tramite.pago_completo:  # Tramite.objects.get(pk=tramite.pk).pago_completo
            return Finalizado(self.tramite)
        else:
            return self


class Finalizado(Estado):
    TIPO = 7
    def __init__(self, tramite):
        super(Finalizado, self).__init__(tramite)


for klass in [Iniciado, Aceptado, Visado, Corregido, Agendado, Inspeccionado, Finalizado]:
    Estado.register(klass)

class Pago(models.Model):
    tramite = models.ForeignKey(Tramite)
    fecha = models.DateField(auto_now=True)
    monto = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        cabecera = '{0} - {1}'.format(self.tramite.pk, self.fecha)
        return cabecera

    @classmethod
    def procesar_pagos(cls, archivo):

        datos = archivo.read()

        #La siguientes linea arma un diccionario para poder recorrer el archivo mejor
        spliter = lambda datos: [ l.split('"')[:2] for l in datos.splitlines()[1:]]

        datos_diccionario = []

        #Esta linea arma una lista de cadenas de la siguiente forma: {'monto': xxxxxx, 'id': xx}
        try:
            for idt, monto in spliter(datos):
                datos_diccionario.append({"id": int(idt[:-1]), "monto": Decimal(monto[1:].replace(".","").replace(",", "."))})

            for linea in datos_diccionario:
                try:
                    monto_pagado = linea['monto']
                    id_tramite = int(linea['id'])
                    tramite = Tramite.objects.get(pk=id_tramite)
                    tramite.calcular_monto_pagado(monto_pagado)
                    p = cls(tramite=tramite, monto=monto_pagado)
                    p.save()
                except Tramite.DoesNotExist:
                    print 'El tramite con numero: {0}, no existe en el sistema. Se ignora su pago.'.format(id_tramite)

        except ValueError:
            print('El archivo cargado no tiene el formato correcto.')
