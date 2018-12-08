#-*- coding:utf-8 -*-

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import  login_required
from .forms import *
from django.contrib import messages
from tipos.forms import *
from obras_particulares.views import *
from tramite.forms import FormularioIniciarTramite
from documento.forms import FormularioDocumentoSetFactory
from documento.forms import metodo
from tramite.models import *
from django.core.mail import send_mail
from persona.models import *
from tramite.models import Tramite, Estado
import re
from datetime import datetime, date, time, timedelta
from dateutil import parser
from django.views.generic.base import TemplateView
from openpyxl import Workbook
from django.http.response import HttpResponse
from django.views.generic import View
from django.conf import settings
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, TableStyle, Table, Image, Spacer
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.pagesizes import letter, A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.graphics.shapes import Drawing, String
from reportlab.graphics import renderPDF
from reportlab.graphics.charts.barcharts import VerticalBarChart
import collections
from django.utils import timezone
from django.http import JsonResponse
from tipos.models import *
from django.db.models import F, Q, When


'''propietario ------------------------------------------------------------------------------------------'''


@login_required(login_url="login")
@grupo_requerido('propietario')
def mostrar_propietario(request):
    usuario = request.user
    perfil = 'css/' + usuario.persona.perfilCSS
    values = {
        "perfil": perfil,
        "ctxtramitespropietario": listado_tramites_propietario(request),
        "ctxtramitesprofesionalpropietario": listado_tramites_cambiar_profesional(request)
    }
    for form_name, submit_name in FORMS_PROPIETARIO:
        KlassForm = FORMS_PROPIETARIO[(form_name, submit_name)]
        if request.method == "POST" and submit_name in request.POST:
            _form = KlassForm(request.POST, request.FILES)
            if _form.is_valid():
                _form.save()
                messages.add_message(request, messages.SUCCESS, "La accion solicitada ha sido ejecutada con exito")
                return redirect(usuario.get_view_name())
            else:
                values["submit_name"] = submit_name
                messages.add_message(request, messages.ERROR, "La accion solicitada no a podido ser ejecutada")
            values[form_name] = _form
        else:
            values[form_name] = KlassForm()
    return render(request, 'persona/propietario/propietario.html', values)

FORMS_PROPIETARIO = {(k.NAME, k.SUBMIT): k for k in [
    FormularioUsuarioCambiarDatos,
    FormularioUsuarioContrasenia,
]}


def listado_tramites_propietario(request):
    pk_persona = request.user.persona.pk
    tramites = Tramite.objects.all()
    tramites_de_propietario = filter(lambda t: (t.propietario.persona.pk == pk_persona), tramites)
    tipos_ag = [11, 21, 28]  # agendados para inspeccion
    dia_hoy = date.today()
    tramites_no_aprobado_o_no_final_o_inspeccion = filter(lambda t: ((datetime.datetime.strftime(t.estado().timestamp, '%d/%m/%Y') == datetime.datetime.strftime(dia_hoy, '%d/%m/%Y') and
                                                                      (t.estado().tipo == tipos_ag[0] or
                                                                       t.estado().tipo == tipos_ag[1] or
                                                                       t.estado().tipo == tipos_ag[2])) or
                                                                     (str(t.estado()) != 'NoFinalizado' or
                                                                      str(t.estado()) != 'NoAprobado')), tramites_de_propietario)

    contexto = {'tramites': tramites_de_propietario, 'tramites_no_aprobado_o_no_final': len(list(tramites_no_aprobado_o_no_final_o_inspeccion))}
    return contexto



def cargar_aprobacion_propietario(request, pk_tramite):
    usuario = request.user
    perfil = 'css/' + usuario.persona.perfilCSS
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    tipos_de_documentos_requeridos = TipoDocumento.get_tipos_documentos_para_momento(TipoDocumento.SOLICITAR_APROBAR_TRAMITE_PROPIETARIO)
    FormularioDocumentoSet = FormularioDocumentoSetFactory(tipos_de_documentos_requeridos)
    inicial = metodo(tipos_de_documentos_requeridos)
    documento_set = FormularioDocumentoSet(initial=inicial)
    id_tramite = int(pk_tramite)
    if request.method == "POST":
        documento_set = FormularioDocumentoSet(request.POST, request.FILES)
        if documento_set.is_valid():
            for docForm in documento_set:
                docForm.save(tramite=tramite)
            if "aprobar_tramite" in request.POST:
                aprobar_tramite_propietario(request, pk_tramite)
    else:
        return render(request, 'persona/propietario/cargar_aprobacion.html', {'tramite': tramite,
                                                                        'ctxdocumentoset': documento_set,
                                                                        'documentos_requeridos': tipos_de_documentos_requeridos,
                                                                        "perfil": perfil})
    return redirect('propietario')


def aprobar_tramite_propietario(request, pk_tramite):
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    try:
        tramite.hacer(tramite.SOLICITAR_APROBAR_TRAMITE_PROPIETARIO, request.user)
        messages.add_message(request, messages.SUCCESS, 'Solicitud de aprobar tramite realizada.')
    except:
        messages.add_message(request, messages.ERROR, 'No se puede solicitar aprobar tramite para este tramite.')
    finally:
        return redirect('propietario')


def cargar_final_de_obra_total_propietario(request, pk_tramite):
    usuario = request.user
    perfil = 'css/' + usuario.persona.perfilCSS
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    tipos_de_documentos_requeridos = TipoDocumento.get_tipos_documentos_para_momento(TipoDocumento.SOLICITAR_FINAL_OBRA_TOTAL_PROPIETARIO)
    FormularioDocumentoSet = FormularioDocumentoSetFactory(tipos_de_documentos_requeridos)
    inicial = metodo(tipos_de_documentos_requeridos)
    documento_set = FormularioDocumentoSet(initial=inicial)
    id_tramite = int(pk_tramite)
    if request.method == "POST":
        documento_set = FormularioDocumentoSet(request.POST, request.FILES)
        if documento_set.is_valid():
            for docForm in documento_set:
                docForm.save(tramite=tramite)
            if "aprobar_final_de_obra_total" in request.POST:
                propietario_solicita_final_obra(request, pk_tramite)
    else:
        return render(request, 'persona/propietario/cargar_final_de_obra_total.html', {'tramite': tramite,
                                                                        'ctxdocumentoset': documento_set,
                                                                        'documentos_requeridos': tipos_de_documentos_requeridos,
                                                                        "perfil": perfil})
    return redirect('propietario')


def propietario_solicita_final_obra(request, pk_tramite):
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    try:
        tramite.hacer(Tramite.SOLICITAR_FINAL_OBRA_TOTAL_PROPIETARIO, request.user)
        messages.add_message(request, messages.SUCCESS, 'Final de obra total solicitado.')
    except:
        messages.add_message(request, messages.ERROR, 'No puede solicitar el final de obra total para ese tramite.')
    finally:
        return redirect('propietario')


def ver_historial_tramite(request, pk_tramite):
    usuario = request.user
    perfil = 'css/' + usuario.persona.perfilCSS
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    contexto0 = {'tramite': tramite}
    pk = int(pk_tramite)
    estados = Estado.objects.all()
    estados_de_tramite = filter(lambda e: (e.tramite.pk == pk), estados)
    contexto1 = {'estados_del_tramite': estados_de_tramite}
    fechas_del_estado = [];
    for est in estados_de_tramite:
        fechas_del_estado.append(est.timestamp.strftime("%d/%m/%Y"))
    return render(request, 'persona/propietario/ver_historial_tramite.html', {"tramite": contexto0,
                                                                              "estadosp": contexto1,
                                                                              "fecha":fechas_del_estado,
                                                                              "perfil": perfil})


def documentos_de_estado(request, pk_estado):
    usuario = request.user
    perfil = 'css/' + usuario.persona.perfilCSS
    estado = get_object_or_404(Estado, pk=pk_estado)
    fecha = estado.timestamp
    fecha_str = datetime.datetime.strftime(fecha, '%d/%m/%Y %H:%M')
    documentos = estado.tramite.documentos.all()
    documentos_fecha = filter(lambda e:(datetime.datetime.strftime(e.fecha, '%d/%m/%Y %H:%M') == fecha_str), documentos)
    contexto= {'documentos_de_fecha': documentos_fecha, "perfil": perfil}
    return render(request, 'persona/propietario/documentos_de_estado.html', contexto)

"""
Metodo que se encarga de devolver un listado con los tramites correspondientes
para que el propietario los pueda cambar de profesional si lo desea
"""
def listado_tramites_cambiar_profesional(request):
    pk_persona = request.user.persona.pk
    tramites = Tramite.objects.all()
    tramites_de_propietario = filter(lambda t: (t.propietario.persona.pk == pk_persona
                                                and str(t.estado()) != 'NoAprobadoSolicitado'
                                                and str(t.estado()) != 'NoAprobado'
                                                and str(t.estado()) != 'AprobadoSolicitadoPorPropietario'
                                                and str(t.estado()) != 'NoFinalObraTotalSolicitado'
                                                and str(t.estado()) != 'AgendadoInspeccionFinal'
                                                and str(t.estado()) != 'InspeccionFinal'
                                                and str(t.estado()) != 'FinalObraTotalSolicitadoPorPropietario'
                                                and str(t.estado()) != 'Finalizado'
                                                and str(t.estado()) != 'Baja'), tramites)
    return tramites_de_propietario


def cambiar_profesional_de_tramite(request, pk_tramite):
    usuario = request.user
    perfil = 'css/' + usuario.persona.perfilCSS
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    usuarios = Usuario.objects.all()
    profesionales = []
    for u in usuarios:
        lista = list(u.groups.values_list('name', flat=True))
        for i in range(len(lista)):
            if lista[i] == 'profesional':
                if u not in profesionales:
                    profesionales.append(u)
    if request.method == "POST" and "cambiar_profesional" in request.POST:
        pers_profesional = get_object_or_404(Persona, pk=request.POST["idempleado"])
        if tramite.profesional.persona.id != pers_profesional.id:
            tramite.cambiar_profesional(pers_profesional.profesional)
            messages.add_message(request, messages.SUCCESS, "El profesional del tramite ha sido cambiado")
        else:
            messages.add_message(request, messages.ERROR, "El profesional del tramite no ha sido cambiado. Selecciono el mismo profesional.")
    else:
        return render(request, 'persona/propietario/cambiar_profesional_de_tramite.html', {'tramite': tramite, "perfil": perfil, 'profesionales': profesionales})
    return redirect('propietario')


'''profesional -------------------------------------------------------------------------------------------'''


@login_required(login_url="login")
@grupo_requerido('profesional')
def mostrar_profesional(request):
    usuario = request.user
    tipos_de_documentos_requeridos = TipoDocumento.get_tipos_documentos_para_momento(TipoDocumento.INICIAR)
    FormularioDocumentoSet = FormularioDocumentoSetFactory(tipos_de_documentos_requeridos)
    inicial = metodo(tipos_de_documentos_requeridos)
    documento_set = FormularioDocumentoSet(initial=inicial)
    tramite_form = FormularioIniciarTramite(initial={'profesional':usuario.persona.profesional.pk})
    propietario_form = FormularioPropietario()
    propietario = None
    if request.method == "POST" and "propietario" in request.POST:
        tramites = Tramite.objects.all()
        t = filter(lambda tramite: (tramite.domicilio == request.POST['domicilio']), tramites)
        if int(usuario.persona.profesional.categoria) <= int(request.POST['tipo_obra']) and len(list(t)) == 0:
            personas = Persona.objects.filter(dni=request.POST["propietario"])
            persona = personas.exists() and personas.first() or None
            documento_set = FormularioDocumentoSet(request.POST, request.FILES)
            propietario_form = FormularioPropietario(request.POST)
            tramite_form = FormularioIniciarTramite(request.POST)
            documento_set = FormularioDocumentoSet(request.POST, request.FILES)
            propietario = propietario_form.obtener_o_crear(persona)
            if propietario is not None and tramite_form.is_valid() and documento_set.is_valid():
                tramite = tramite_form.save(propietario=propietario, commit=False)
                lista = []
                for docForm in documento_set:
                    lista.append(docForm.save(commit=False))
                Tramite.new(usuario, propietario, usuario.persona.profesional, request.POST['tipo_obra'], request.POST['medidas'], request.POST['domicilio'], lista, request.POST['destino_obra'])
                tramite_form = FormularioIniciarTramite(initial={'profesional':usuario.persona.profesional.pk})
                propietario_form = None
                messages.add_message(request, messages.SUCCESS,'Solicitud de iniciar tramitre realizada con exito.')
            else:
                messages.add_message(request, messages.ERROR, 'Propietario no existe, debe darlo de alta para iniciar al tramite.')
        else:
            propietario_form = None
            if int(usuario.persona.profesional.categoria) < int(request.POST['tipo_obra']):
                messages.add_message(request, messages.ERROR,
                                     'Categoria del profesional no es suficiente para el tipo de tramite que desea iniciar.')
            else:
                messages.add_message(request, messages.ERROR,
                                     'Ya existe un tramite para este domicilio.')
    else:
        propietario_form = None
    perfil = 'css/' + usuario.persona.perfilCSS
    values = {
        "perfil": perfil,
        'documentos_requeridos': tipos_de_documentos_requeridos,
        'ctxtramitesprofesional': listado_tramites_de_profesional(request),
        'tramite_form': tramite_form,
        'propietario_form': propietario_form,
        'documento_set': documento_set,
        'ctxtramcorregidos': tramites_corregidos(request)
    }
    for form_name, submit_name in FORMS_ADMINISTRATIVO:
        KlassForm = FORMS_ADMINISTRATIVO[(form_name, submit_name)]
        if request.method == "POST" and submit_name in request.POST:
            _form = KlassForm(request.POST, request.FILES)
            if _form.is_valid():
                _form.save()
                messages.add_message(request, messages.SUCCESS,"La accion solicitada ha sido ejecutada con exito")
                return redirect(usuario.get_view_name())
            else:
                values["submit_name"] = submit_name
                messages.add_message(request, messages.ERROR, "La accion solicitada no a podido ser ejecutada")
            values[form_name] = _form
        else:
            values[form_name] = KlassForm()
    return render(request, 'persona/profesional/profesional.html', values)

FORMS_PROFESIONAL = {(k.NAME, k.SUBMIT): k for k in [
    FormularioUsuarioCambiarDatos,
    FormularioUsuarioContrasenia,
]}


def listado_tramites_de_profesional(request):
    tramites = Tramite.objects.all()
    personas = Persona.objects.all()
    usuario = request.user
    lista_de_persona_que_esta_logueada = filter(lambda persona: (persona.usuario is not None and persona.usuario == usuario), personas)
    persona = list(lista_de_persona_que_esta_logueada).pop()
    profesional = persona.get_profesional()
    tramites_de_profesional = filter(lambda tramite: (tramite.profesional == profesional), tramites)
    tipos_ag = [11, 21, 28]  # agendados para inspeccion
    tipo_ip = 12  # primer inspeccion
    tramites_inspecion_dia = filter(lambda t: ((datetime.datetime.strftime(t.estado().timestamp, '%d/%m/%Y') == datetime.datetime.strftime(datetime.datetime.now(), '%d/%m/%Y') and
                                               (t.estado().tipo == tipos_ag[0] or
                                                t.estado().tipo == tipos_ag[1] or
                                                t.estado().tipo == tipos_ag[2])) or (t.estado().tipo == tipo_ip and t.monto_pagado and t.monto_pagado >= (t.monto_a_pagar/12))), tramites_de_profesional)
    contexto = {'tramites_de_profesional': tramites_de_profesional, 'tramites_inspeccion_dia': len(list(tramites_inspecion_dia))}
    return contexto


def tramites_corregidos(request):
    tramites = Tramite.objects.all()
    personas = Persona.objects.all()
    usuario = request.user
    lista_de_persona_que_esta_logueada = filter(lambda persona: (persona.usuario is not None and persona.usuario == usuario), personas)
    persona = list(lista_de_persona_que_esta_logueada).pop()
    profesional = persona.get_profesional()
    tramites_de_profesional = filter(lambda tramite: (tramite.profesional == profesional), tramites)
    tram_corregidos = filter(lambda tramite: (str(tramite.estado()) == 'ConCorrecciones' or
                                              str(tramite.estado()) == 'ConCorreccionesDeVisado' or
                                              str(tramite.estado()) == 'ConCorreccionesDePrimerInspeccion' or
                                              str(tramite.estado()) == 'ConCorreccionesDeInspeccion' or
                                              str(tramite.estado()) == 'ConCorreccionesDeInspeccionFinal'),
                             tramites_de_profesional)
    contexto = {'tramites': tram_corregidos, 'len_tramites': len(list(tram_corregidos))}
    return contexto


def ver_documentos_tramite_profesional(request, pk_tramite):
    usuario = request.user
    perfil = 'css/' + usuario.persona.perfilCSS
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    contexto0 = {'tramite': tramite}
    pk = int(pk_tramite)
    estados = Estado.objects.all()
    estados_de_tramite = filter(lambda e: (e.tramite.pk == pk), estados)
    contexto1 = {'estados_del_tramite': estados_de_tramite}
    fechas_del_estado = []
    for est in estados_de_tramite:
        fechas_del_estado.append(est.timestamp.strftime("%d/%m/%Y"))
    return render(request, 'persona/profesional/vista_de_documentos.html', {"tramite": contexto0,
                                                                            "estadosp": contexto1,
                                                                            "fecha":fechas_del_estado,
                                                                            "perfil": perfil})


def profesional_solicita_aprobar_tramite(request, pk_tramite):
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    try:
        if str(tramite.estado()) != 'NoAprobado':
            tramite.hacer(Tramite.SOLICITAR_APROBAR_TRAMITE, request.user)
            messages.add_message(request, messages.SUCCESS, 'Solicitud de aprobar tramite realizada.')
        else:
            messages.add_message(request, messages.ERROR, 'No puede solicitar aprobar tramite para ese tramite.')
    except:
        messages.add_message(request, messages.ERROR, 'No puede solicitar aprobar tramite para ese tramite.')
    finally:
        return redirect('profesional')


def cargar_no_aprobar_profesional(request, pk_tramite):
    usuario = request.user
    perfil = 'css/' + usuario.persona.perfilCSS
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    tipos_de_documentos_requeridos = TipoDocumento.get_tipos_documentos_para_momento(TipoDocumento.SOLICITAR_NO_APROBAR_TRAMITE)
    FormularioDocumentoSet = FormularioDocumentoSetFactory(tipos_de_documentos_requeridos)
    inicial = metodo(tipos_de_documentos_requeridos)
    documento_set = FormularioDocumentoSet(initial=inicial)
    id_tramite = int(pk_tramite)
    if request.method == "POST":
        documento_set = FormularioDocumentoSet(request.POST, request.FILES)
        if documento_set.is_valid():
            for docForm in documento_set:
                docForm.save(tramite=tramite)
            if "no_aprobar_tramite" in request.POST:
                profesional_solicita_no_aprobar_tramite(request, pk_tramite)
    else:
        return render(request, 'persona/profesional/cargar_no_aprobacion.html', {'tramite': tramite,
                                                                        'ctxdocumentoset': documento_set,
                                                                        'documentos_requeridos': tipos_de_documentos_requeridos,
                                                                        "perfil": perfil})
    return redirect('profesional')


def profesional_solicita_no_aprobar_tramite(request, pk_tramite):
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    try:
        tramite.hacer(Tramite.SOLICITAR_NO_APROBAR_TRAMITE, request.user)
        messages.add_message(request, messages.SUCCESS, 'Solicitud de no aprobar tramite realizada.')
    except:
        messages.add_message(request, messages.ERROR, 'No puede solicitar no aprobar tramite para ese tramite.')
    finally:
        return redirect('profesional')


def cargar_final_de_obra_total_profesional(request, pk_tramite):
    usuario = request.user
    perfil = 'css/' + usuario.persona.perfilCSS
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    tipos_de_documentos_requeridos = TipoDocumento.get_tipos_documentos_para_momento(TipoDocumento.SOLICITAR_FINAL_OBRA_TOTAL)
    FormularioDocumentoSet = FormularioDocumentoSetFactory(tipos_de_documentos_requeridos)
    inicial = metodo(tipos_de_documentos_requeridos)
    documento_set = FormularioDocumentoSet(initial=inicial)
    id_tramite = int(pk_tramite)
    if request.method == "POST":
        documento_set = FormularioDocumentoSet(request.POST, request.FILES)
        if documento_set.is_valid():
            for docForm in documento_set:
                docForm.save(tramite=tramite)
            if "aprobar_final_de_obra_total" in request.POST:
                profesional_solicita_final_obra(request, pk_tramite)
    else:
        return render(request, 'persona/profesional/cargar_final_de_obra_total.html', {'tramite': tramite,
                                                                        'ctxdocumentoset': documento_set,
                                                                        'documentos_requeridos': tipos_de_documentos_requeridos,
                                                                        "perfil": perfil})
    return redirect('profesional')


def profesional_solicita_final_obra(request, pk_tramite):
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    try:
        if str(tramite.estado()) != 'NoFinalizado':
            tramite.hacer(Tramite.SOLICITAR_FINAL_OBRA_TOTAL, request.user)
            messages.add_message(request, messages.SUCCESS, 'Final de obra solicitado.')
        else:
            messages.add_message(request, messages.ERROR, 'No puede solicitar el final de obra para ese tramite.')
    except:
        messages.add_message(request, messages.ERROR, 'No puede solicitar el final de obra para ese tramite.')
    finally:
        return redirect('profesional')


def cargar_no_final_de_obra_total_profesional(request, pk_tramite):
    usuario = request.user
    perfil = 'css/' + usuario.persona.perfilCSS
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    tipos_de_documentos_requeridos = TipoDocumento.get_tipos_documentos_para_momento(TipoDocumento.SOLICITAR_NO_FINAL_OBRA_TOTAL)
    FormularioDocumentoSet = FormularioDocumentoSetFactory(tipos_de_documentos_requeridos)
    inicial = metodo(tipos_de_documentos_requeridos)
    documento_set = FormularioDocumentoSet(initial=inicial)
    id_tramite = int(pk_tramite)
    if request.method == "POST":
        documento_set = FormularioDocumentoSet(request.POST, request.FILES)
        if documento_set.is_valid():
            for docForm in documento_set:
                docForm.save(tramite=tramite)
            if "no_aprobar_final_de_obra_total" in request.POST:
                profesional_solicita_no_final_obra(request, pk_tramite)
    else:
        return render(request, 'persona/profesional/cargar_no_final_de_obra_total.html', {'tramite': tramite,
                                                                        'ctxdocumentoset': documento_set,
                                                                        'documentos_requeridos': tipos_de_documentos_requeridos,
                                                                        "perfil": perfil})
    return redirect('profesional')


def profesional_solicita_no_final_obra(request, pk_tramite):
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    try:
        tramite.hacer(Tramite.SOLICITAR_NO_FINAL_OBRA_TOTAL, request.user)
        messages.add_message(request, messages.SUCCESS, 'No Final de obra solicitado.')
    except:
        messages.add_message(request, messages.ERROR, 'No puede solicitar el no final de obra para ese tramite.')
    finally:
        return redirect('profesional')


def profesional_solicita_final_obra_parcial(request, pk_tramite):
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    try:
        estados = Estado.objects.all()
        tipo = 17
        estado = filter(lambda e: (e.tipo == tipo and str(e.tramite.pk) == str(pk_tramite)), estados)
        if len(list(estado)) == 0:
            tramite.hacer(Tramite.SOLICITAR_FINAL_OBRA_PARCIAL, request.user)
            messages.add_message(request, messages.SUCCESS, 'Final de obra parcial solicitado.')
        else:
            messages.add_message(request, messages.ERROR, 'No puede solicitar el final de obra parcial para ese tramite.')
    except:
        messages.add_message(request, messages.ERROR, 'No puede solicitar el final de obra parcial para ese tramite.')
    finally:
        return redirect('profesional')


def ver_documentos_corregidos(request, pk_tramite):
    usuario = request.user
    perfil = 'css/' + usuario.persona.perfilCSS
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    tipos_de_documentos_requeridos = TipoDocumento.get_tipos_documentos_para_momento(TipoDocumento.INGRESAR_CORRECCIONES)
    FormularioDocumentoSet = FormularioDocumentoSetFactory(tipos_de_documentos_requeridos)
    inicial = metodo(tipos_de_documentos_requeridos)
    documento_set = FormularioDocumentoSet(initial=inicial)
    if request.method == "POST" and "enviar_correcciones" in request.POST:
        documento_set = FormularioDocumentoSet(request.POST, request.FILES)
        if documento_set.is_valid():
            for docForm in documento_set:
                docForm.save(tramite=tramite)
            enviar_correcciones(request, pk_tramite)
    else:
        return render(request, 'persona/profesional/ver_documentos_corregidos.html', {'tramite': tramite,
                                                                                      "perfil": perfil,
                                                                                      'ctxdocumentoset': documento_set,
                                                                                      'documentos_requeridos': tipos_de_documentos_requeridos,
                                                                                      })
    return redirect('profesional')


def enviar_correcciones(request, pk_tramite):
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    tramite.hacer(tramite.INGRESAR_CORRECCIONES, request.user)
    messages.add_message(request, messages.SUCCESS, 'Tramite con documentos corregidos y enviados')
    return redirect('profesional')


def documento_de_estado(request, pk_estado):
    usuario = request.user
    perfil = 'css/' + usuario.persona.perfilCSS
    estado = get_object_or_404(Estado, pk=pk_estado)
    fecha = estado.timestamp
    fecha_str = datetime.datetime.strftime(fecha, '%d/%m/%Y %H:%M')
    documentos = estado.tramite.documentos.all()
    documentos_fecha = filter(lambda e:(datetime.datetime.strftime(e.fecha, '%d/%m/%Y %H:%M') == fecha_str), documentos)
    contexto= {'documentos_de_fecha': documentos_fecha, "perfil": perfil}
    return render(request, 'persona/profesional/documento_de_estado.html', contexto)


'''administrativo ---------------------------------------------------------------------------------------'''


@login_required(login_url="login")
@grupo_requerido('administrativo')
def mostrar_administrativo(request):
    usuario = request.user
    perfil = 'css/' + usuario.persona.perfilCSS
    values = {
        "perfil": perfil,
        "ctxprofesional": profesional_list(),
        "ctxpropietario": propietario_list(),
        "ctxtramitesiniciados": listado_de_tramites_iniciados(),
        "ctxtramitescorregidos": tramite_corregidos_list(),
        "ctxsolicitudesfinalobra": solicitud_final_obra_list(),
        "ctxsolicitudesaprobacion": solicitud_aprobacion_list(),
        "ctxsolicitudesnoaprobacion": solicitud_no_aprobacion_list(),
        "ctxpago": registrar_pago_tramite(request),
        "ctxtramitesvencidos": listado_tramites_vencidos()
    }
    for form_name, submit_name in FORMS_ADMINISTRATIVO:
        KlassForm = FORMS_ADMINISTRATIVO[(form_name, submit_name)]
        if request.method == "POST" and submit_name in request.POST:
            _form = KlassForm(request.POST, request.FILES)
            if _form.is_valid():
                _form.save()
                messages.add_message(request, messages.SUCCESS, "La accion solicitada ha sido ejecutada con exito")
                return redirect(usuario.get_view_name())
            else:
                values["submit_name"] = submit_name
                messages.add_message(request, messages.ERROR, "La accion solicitada no a podido ser ejecutada")
            values[form_name] = _form
        else:
            values[form_name] = KlassForm()
    return render(request, 'persona/administrativo/administrativo.html', values)


FORMS_ADMINISTRATIVO = {(k.NAME, k.SUBMIT): k for k in [
    FormularioUsuarioGrupo,
    FormularioUsuarioCambiarDatos,
    FormularioUsuarioContrasenia,
]}


def profesional_list():
    personas = Persona.objects.all()
    profesionales = filter(lambda persona: (persona.usuario is None and persona.profesional is not None), personas)
    contexto = {'personas': profesionales,
                'len_personas': len(list(profesionales))
                }
    return contexto


def propietario_list():
    propietarios = Propietario.objects.all()
    propietarios_sin_usuario = filter(lambda propietario: (propietario.persona.usuario is None and propietario.persona is not None ), propietarios)
    contexto = {'propietarios': propietarios_sin_usuario,
                'len_propietarios': len(list(propietarios_sin_usuario))
                }
    return contexto


def listado_de_tramites_iniciados():
    argumentos = [Iniciado, ConCorreccionesRealizadas]
    tramites = Tramite.objects.en_estado(argumentos)
    contexto = {'tramites': tramites}
    return contexto


def tramite_corregidos_list():
    tramites = Tramite.objects.all()
    contexto = {'tramites': tramites}
    return contexto


def solicitud_final_obra_list():
    argumentos = [InspeccionFinal, FinalObraTotalSolicitadoPorPropietario]
    tramites = Tramite.objects.en_estado(argumentos)
    contexto = {'tramites': tramites}
    return contexto


def solicitud_aprobacion_list():
    argumentos = [AprobadoSolicitado, AprobadoSolicitadoPorPropietario]
    tramites = Tramite.objects.en_estado(argumentos)
    contexto = {'tramites': tramites}
    return contexto


def solicitud_no_aprobacion_list():
    tramites = Tramite.objects.en_estado(NoAprobadoSolicitado)
    contexto = {'tramites': tramites}
    return contexto


def listado_tramites_vencidos():
    argumentos_ap = [Iniciado, Aceptado, AgendadoParaVisado, Visado, AgendadoPrimerInspeccion, PrimerInspeccion,
                  NoAprobadoSolicitado, NoAprobado]
    tramites_ap = Tramite.objects.en_estado(argumentos_ap)
    argumentos_fo = [AprobadoSolicitado, Aprobado, NoAprobadoSolicitado, NoAprobado, AprobadoSolicitadoPorPropietario,
                  AprobadoPorPropietario, AgendadoInspeccion, Inspeccionado, FinalObraParcialSolicitado]
    tramites_fo = Tramite.objects.en_estado(argumentos_fo)
    estados = Estado.objects.all()
    tipo = 1
    estados_iniciado = filter(lambda e: (e.tipo == tipo), estados)
    tramites_vencidos = []
    for t in tramites_ap:
        for e in estados_iniciado:
            if e.tramite == t and (e.timestamp + timedelta(days=60)).strftime("%Y/%m/%d") < datetime.datetime.now().strftime("%Y/%m/%d"):
                tramites_vencidos.append(t)
    tramites_vencidos_no_pagados_no_renovados = []
    for tr in tramites_vencidos:
        if not tr.monto_pagado or tr.monto_pagado < (tr.monto_a_pagar / 12):
            tramites_vencidos_no_pagados_no_renovados.append(tr)
    tipoFOPS = 17
    for t in tramites_fo:
        estado_t = filter(lambda e: (e.tipo == tipoFOPS and str(e.tramite.pk) == str(t.pk)), estados)
        for e in estados_iniciado:
            if e.tramite == t and len(list(estado_t)) == 0 and (e.timestamp + timedelta(days=1095)).strftime("%Y/%m/%d") < datetime.datetime.now().strftime("%Y/%m/%d"):
                tramites_vencidos_no_pagados_no_renovados.append(t)
            elif e.tramite == t and len(list(estado_t)) > 0 and (e.timestamp + timedelta(days=1825)).strftime("%Y/%m/%d") < datetime.datetime.now().strftime("%Y/%m/%d"):
                tramites_vencidos_no_pagados_no_renovados.append(t)
    contexto = {'tramites': tramites_vencidos_no_pagados_no_renovados, 'tramites_vencidos_no_pagados_no_renovados': len(tramites_vencidos)}
    return contexto


def registrar_pago_tramite(request):
    if request.method == "POST":
        archivo_pago_form = FormularioArchivoPago(request.POST, request.FILES)
        if archivo_pago_form.is_valid():
            Pago.procesar_pagos(request.FILES['pagos'])
    else:
        archivo_pago_form = FormularioArchivoPago()
    return archivo_pago_form


def crear_usuario(request, pk_persona):
    usuario = request.user
    persona = get_object_or_404(Persona, pk=pk_persona)
    creado, password, usuario_creado = persona.crear_usuario()
    if creado:
        messages.add_message(request, messages.SUCCESS, 'Profesional fue aceptado y su usuario creado.')
        send_mail(
            'Usuario habilitado',
            'Usted ya puede acceder al sistema: Nombre de usuario: '+persona.mail+' password: '+password,
            'infosopunpsjb@gmail.com',
            [persona.mail],
            fail_silently=False,
        )
    else:
        print("Mando correo informando que se cambio algo en su cuenta de usuario")
    return redirect(usuario.get_view_name())


def cargar_final_de_obra_total(request, pk_tramite):
    usuario = request.user
    perfil = 'css/' + usuario.persona.perfilCSS
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    estados = Estado.objects.all()
    tipoFOS = 16
    tipos_de_documentos_requeridos = []
    estadoFOS = filter(lambda e: (e.tipo == tipoFOS and str(e.tramite.pk) == str(pk_tramite)), estados)
    if len(list(estadoFOS)) > 0:
        tipos_de_documentos_requeridos = TipoDocumento.get_tipos_documentos_para_momento(TipoDocumento.FINALIZAR)
    tipoNFOS = 18
    estadoNFOS = filter(lambda e: (e.tipo == tipoNFOS and str(e.tramite.pk) == str(pk_tramite)), estados)
    if len(list(estadoNFOS)) > 0:
        tipos_de_documentos_requeridos = TipoDocumento.get_tipos_documentos_para_momento(TipoDocumento.NO_FINALIZAR)
    if str(tramite.estado()) == 'FinalObraTotalSolicitadoPorPropietario':
        tipos_de_documentos_requeridos = TipoDocumento.get_tipos_documentos_para_momento(TipoDocumento.FINALIZAR)
    FormularioDocumentoSet = FormularioDocumentoSetFactory(tipos_de_documentos_requeridos)
    inicial = metodo(tipos_de_documentos_requeridos)
    documento_set = FormularioDocumentoSet(initial=inicial)
    id_tramite = int(pk_tramite)
    if request.method == "POST":
        documento_set = FormularioDocumentoSet(request.POST, request.FILES)
        if documento_set.is_valid():
            for docForm in documento_set:
                docForm.save(tramite=tramite)
            if "aprobar_final_de_obra_total" in request.POST:
                habilitar_final_obra(request, pk_tramite)
    else:
        return render(request, 'persona/administrativo/cargar_final_de_obra_total.html', {'tramite': tramite,
                                                                        'ctxdocumentoset': documento_set,
                                                                        'documentos_requeridos': tipos_de_documentos_requeridos,
                                                                        "perfil": perfil})
    return redirect('administrativo')


def habilitar_final_obra(request, pk_tramite):
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    try:
        estados = Estado.objects.all()
        tipoFOS = 16
        estadoFOS = filter(lambda e: (e.tipo == tipoFOS and str(e.tramite.pk) == str(pk_tramite)), estados)
        if len(list(estadoFOS)) > 0:
            tramite.hacer(tramite.FINALIZAR, request.user)
            messages.add_message(request, messages.SUCCESS, 'Final de obra aprobado.')
        tipoNFOS = 18
        estadoNFOS = filter(lambda e: (e.tipo == tipoNFOS and str(e.tramite.pk) == str(pk_tramite)), estados)
        if len(list(estadoNFOS)) > 0 and str(tramite.estado()) != 'FinalObraTotalSolicitadoPorPropietario':
            tramite.hacer(tramite.NO_FINALIZAR, request.user)
            messages.add_message(request, messages.SUCCESS, 'No Final de obra aprobado.')
        if len(list(estadoNFOS)) > 0 and str(tramite.estado()) == 'FinalObraTotalSolicitadoPorPropietario':
            tramite.hacer(tramite.FINALIZAR, request.user)
            messages.add_message(request, messages.SUCCESS, 'Final de obra total solicitado por propietario aprobado.')
    except:
        messages.add_message(request, messages.ERROR, 'No se puede otorgar final de obra total para ese tramite.')
    finally:
        return redirect('administrativo')


def cargar_aprobacion(request, pk_tramite):
    usuario = request.user
    perfil = 'css/' + usuario.persona.perfilCSS
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    tipos_de_documentos_requeridos = TipoDocumento.get_tipos_documentos_para_momento(TipoDocumento.APROBAR_TRAMITE)
    FormularioDocumentoSet = FormularioDocumentoSetFactory(tipos_de_documentos_requeridos)
    inicial = metodo(tipos_de_documentos_requeridos)
    documento_set = FormularioDocumentoSet(initial=inicial)
    id_tramite = int(pk_tramite)
    if request.method == "POST":
        documento_set = FormularioDocumentoSet(request.POST, request.FILES)
        if documento_set.is_valid():
            for docForm in documento_set:
                docForm.save(tramite=tramite)
            if "aprobar_tramite" in request.POST:
                aprobar_tramite(request, pk_tramite)
    else:
        return render(request, 'persona/administrativo/cargar_aprobacion.html', {'tramite': tramite,
                                                                        'ctxdocumentoset': documento_set,
                                                                        'documentos_requeridos': tipos_de_documentos_requeridos,
                                                                        "perfil": perfil})
    return redirect('administrativo')


def aprobar_tramite(request, pk_tramite):
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    try:
        tramite.hacer(tramite.APROBAR_TRAMITE, request.user)
        messages.add_message(request, messages.SUCCESS, 'Tramite aprobado.')
    except:
        messages.add_message(request, messages.ERROR, 'No se puede aprobar este tramite.')
    finally:
        return redirect('administrativo')


def cargar_no_aprobacion(request, pk_tramite):
    usuario = request.user
    perfil = 'css/' + usuario.persona.perfilCSS
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    tipos_de_documentos_requeridos = TipoDocumento.get_tipos_documentos_para_momento(TipoDocumento.APROBAR_TRAMITE)
    FormularioDocumentoSet = FormularioDocumentoSetFactory(tipos_de_documentos_requeridos)
    inicial = metodo(tipos_de_documentos_requeridos)
    documento_set = FormularioDocumentoSet(initial=inicial)
    id_tramite = int(pk_tramite)
    if request.method == "POST":
        documento_set = FormularioDocumentoSet(request.POST, request.FILES)
        if documento_set.is_valid():
            for docForm in documento_set:
                docForm.save(tramite=tramite)
            if "no_aprobar_tramite" in request.POST:
                no_aprobar_tramite(request, pk_tramite)
    else:
        return render(request, 'persona/administrativo/cargar_no_aprobacion.html', {'tramite': tramite,
                                                                        'ctxdocumentoset': documento_set,
                                                                        'documentos_requeridos': tipos_de_documentos_requeridos,
                                                                        "perfil": perfil})
    return redirect('administrativo')


def no_aprobar_tramite(request, pk_tramite):
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    try:
        tramite.hacer(tramite.NO_APROBAR_TRAMITE, request.user)
        messages.add_message(request, messages.SUCCESS, 'Tramite no aprobado.')
    except:
        messages.add_message(request, messages.ERROR, 'No se puede no aprobar este tramite.')
    finally:
        return redirect('administrativo')


def aceptar_tramite(request, pk_tramite):
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    tramite.hacer(tramite.ACEPTAR, request.user)
    messages.add_message(request, messages.SUCCESS, "Tramite aceptado")
    return redirect('administrativo')


def rechazar_tramite(request, pk_tramite):
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    tramite.hacer(tramite.CORREGIR, request.user, request.GET["msg"])
    messages.add_message(request, messages.SUCCESS, 'Tramite rechazado.')
    return redirect('administrativo')


def dar_baja_tramite(request, pk_tramite):
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    print(tramite.estado().tipo )
    if tramite.estado().tipo < 19:
        obs = "Tramite dado de baja. Se ha vencido el plazo de pago del permiso de construccion"
    else:
        obs = "Tramite dado de baja. Se ha vencido el plazo de construccion de la obra"
    tramite.hacer(tramite.DAR_DE_BAJA, request.user, obs)
    messages.add_message(request, messages.SUCCESS, obs)
    return redirect('administrativo')


def ver_un_certificado(request, pk_persona):
    usuario = request.user
    perfil = 'css/' + usuario.persona.perfilCSS
    persona = get_object_or_404(Persona, pk=pk_persona)
    return render(request, 'persona/administrativo/ver_certificado_profesional.html', {'persona': persona,
                                                                                       "perfil": perfil})


def ver_documentos_tramite_administrativo(request, pk_tramite):
    usuario = request.user
    perfil = 'css/' + usuario.persona.perfilCSS
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    return render(request, 'persona/administrativo/vista_de_documentos_administrativo.html', {'tramite': tramite,
                                                                                              "perfil": perfil})


'''visador -----------------------------------------------------------------------------------------------'''


@login_required(login_url="login")
@grupo_requerido('visador')
def mostrar_visador(request):
    usuario = request.user
    perfil = 'css/' + usuario.persona.perfilCSS
    values = {
        "perfil": perfil,
        "ctxtramaceptado": tramites_aceptados(),
        "ctxtramagendado": tramites_agendados(request),
        "ctxtramvisados": tramites_visados(request),
    }
    for form_name, submit_name in FORMS_VISADOR:
        KlassForm = FORMS_VISADOR[(form_name, submit_name)]
        if request.method == "POST" and submit_name in request.POST:
            _form = KlassForm(request.POST, request.FILES)
            if _form.is_valid():
                _form.save()
                messages.add_message(request, messages.SUCCESS, "La accion solicitada ha sido ejecutada con exito")
                return redirect(usuario.get_view_name())
            else:
                values["submit_name"] = submit_name
                messages.add_message(request, messages.ERROR, "La accion solicitada no a podido ser ejecutada")
            values[form_name] = _form
        else:
            values[form_name] = KlassForm()
    return render(request, 'persona/visador/visador.html', values)

FORMS_VISADOR = {(k.NAME, k.SUBMIT): k for k in [
    FormularioUsuarioGrupo,
    FormularioUsuarioCambiarDatos,
    FormularioUsuarioContrasenia,
]}


def tramites_aceptados():
    argumentos = [Aceptado, CorreccionesDeVisadoRealizadas]
    aceptados = Tramite.objects.en_estado(argumentos)
    contexto = {'tramites': aceptados}
    return contexto


def agendar_tramite_para_visado(request, pk_tramite):
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    tramite.hacer(Tramite.AGENDAR_VISADO, request.user)
    messages.add_message(request, messages.SUCCESS, "El visado ha sido agendado")
    return redirect('visador')


def tramites_agendados(request):
    usuario = request.user
    argumentos = [AgendadoParaVisado]
    agendados = Tramite.objects.en_estado(argumentos)
    tramites_del_visador = filter(lambda t: t.estado().usuario == usuario, agendados)
    contexto = {'tramites': tramites_del_visador, 'len_tramites_del_visador': len(list(tramites_del_visador))}
    return contexto


def tramites_visados(request):
    usuario = request.user
    estados = Estado.objects.all()
    tipos = [5, 8]
    estados_visado = filter(lambda estado: (estado.usuario is not None and estado.usuario == usuario and (estado.tipo == tipos[0] or estado.tipo == tipos[1])), estados)
    contexto = {'estados': estados_visado}
    return contexto


def ver_documentos_para_visado(request, pk_tramite):
    usuario = request.user
    perfil = 'css/' + usuario.persona.perfilCSS
    tipos_de_documentos_requeridos = TipoDocumento.get_tipos_documentos_para_momento(TipoDocumento.VISAR)
    FormularioDocumentoSet = FormularioDocumentoSetFactory(tipos_de_documentos_requeridos)
    inicial = metodo(tipos_de_documentos_requeridos)
    documento_set = FormularioDocumentoSet(initial=inicial)
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    if request.method == "POST":
        observacion = request.POST["observaciones"]
        tram = request.POST['tram']
        monto_permiso = tramite.medidas * tramite.tipo_obra.valor_de_superficie
        documento_set = FormularioDocumentoSet(request.POST, request.FILES)
        if documento_set.is_valid():
            for docForm in documento_set:
                docForm.save(tramite=tramite)
            if "Aprobar el visado" in request.POST:
                aprobar_visado(request, tram, monto_permiso)
            else:
                no_aprobar_visado(request, tram, observacion)
    else:
        return render(request, 'persona/visador/ver_documentos_tramite.html', {'tramite': tramite,
                                                                               'ctxdoc': documento_set,
                                                                               'documentos_requeridos': tipos_de_documentos_requeridos,
                                                                               "perfil": perfil})
    return redirect('visador')


def ver_documentos_visados(request, pk_estado):
    usuario = request.user
    perfil = 'css/' + usuario.persona.perfilCSS
    estado = get_object_or_404(Estado, pk=pk_estado)
    fecha = estado.timestamp
    fecha_str = datetime.datetime.strftime(fecha, '%d/%m/%Y %H:%M')
    documentos = estado.tramite.documentos.all()
    documentos_fecha = filter(lambda e: (datetime.datetime.strftime(e.fecha, '%d/%m/%Y %H:%M') == fecha_str), documentos)
    contexto = {'documentos_de_fecha': documentos_fecha, "perfil": perfil}
    return render(request, 'persona/visador/ver_documentos_visados.html', contexto)


def aprobar_visado(request, pk_tramite, monto):
    usuario = request.user
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    tramite.hacer(tramite.VISAR, usuario)
    tramite.monto_a_pagar= monto
    tramite.save()
    messages.add_message(request, messages.SUCCESS, 'Tramite visado aprobado')
    return redirect('visador')


def no_aprobar_visado(request, pk_tramite, observacion):
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    obs = observacion
    tramite.hacer(tramite.CORREGIR, request.user, obs)
    messages.add_message(request, messages.SUCCESS, 'Tramite con visado no aprobado')
    return redirect('visador')


'''inspector --------------------------------------------------------------------------------------------'''


@login_required(login_url="login")
@grupo_requerido('inspector')
def mostrar_inspector(request):
    usuario = request.user
    perfil = 'css/' + usuario.persona.perfilCSS
    values = {
        "perfil": perfil,
        "ctxtramitesvisadosyconinspeccion": tramites_visados_y_con_inspeccion(),
        "ctxtramitesinspeccionados": tramites_inspeccionados_por_inspector(request),
        "ctxtramitesagendados": tramites_agendados_por_inspector(request)
    }
    for form_name, submit_name in FORMS_INSPECTOR:
        KlassForm = FORMS_INSPECTOR[(form_name, submit_name)]
        if request.method == "POST" and submit_name in request.POST:
            _form = KlassForm(request.POST, request.FILES)
            if _form.is_valid():
                _form.save()
                messages.add_message(request, messages.SUCCESS, "La accion solicitada ha sido ejecutada con exito")
                return redirect(usuario.get_view_name())
            else:
                values["submit_name"] = submit_name
                messages.add_message(request, messages.ERROR, "La accion solicitada no a podido ser ejecutada")
            values[form_name] = _form
        else:
            values[form_name] = KlassForm()
    return render(request, 'persona/inspector/inspector.html', values)

FORMS_INSPECTOR = {(k.NAME, k.SUBMIT): k for k in [
    FormularioUsuarioGrupo,
    FormularioUsuarioCambiarDatos,
    FormularioUsuarioContrasenia,
]}


def tramites_visados_y_con_inspeccion():
    argumentos = [Visado, Inspeccionado, Aprobado, AprobadoPorPropietario, FinalObraParcialSolicitado,
                  CorreccionesDePrimerInspeccionRealizadas, CorreccionesDeInspeccionRealizadas]
    tramites = Tramite.objects.en_estado(argumentos)
    return tramites


def tramites_inspeccionados_por_inspector(request):
    usuario = request.user
    estados = Estado.objects.all()
    tipos = [9, 12, 19, 22]
    estados_inspeccionados = filter(lambda estado: (estado.usuario is not None and estado.usuario == usuario and
                                                    (estado.tipo == tipos[0] or
                                                     estado.tipo == tipos[1] or
                                                     estado.tipo == tipos[2] or
                                                     estado.tipo == tipos[3])), estados)
    return estados_inspeccionados


def tramites_agendados_por_inspector(request):
    usuario = request.user
    argumentos = [AgendadoPrimerInspeccion, AgendadoInspeccion]
    tramites = Tramite.objects.en_estado(argumentos)
    tramites_del_inspector = filter(lambda t: t.estado().usuario == usuario, tramites)
    tramites_del_inspector_del_dia = filter(lambda t: datetime.datetime.strftime(t.estado().fecha, '%Y-%m-%d') == datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d'), tramites_del_inspector)
    contexto = {'tramites': tramites_del_inspector, 'len_tramites': len(list(tramites_del_inspector_del_dia))}
    return contexto

def agendar_tramite(request, pk_tramite):
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    fecha = parser.parse(request.GET["msg"])
    tramite.hacer(Tramite.AGENDAR_INSPECCION, request.user, fecha)
    messages.add_message(request, messages.SUCCESS, "La inspeccion ha sido agendada")
    return redirect('inspector')


def cargar_inspeccion(request, pk_tramite):
    usuario = request.user
    perfil = 'css/' + usuario.persona.perfilCSS
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    tipos_de_documentos_requeridos = TipoDocumento.get_tipos_documentos_para_momento(TipoDocumento.APROBAR_INSPECCION)
    FormularioDocumentoSet = FormularioDocumentoSetFactory(tipos_de_documentos_requeridos)
    inicial = metodo(tipos_de_documentos_requeridos)
    documento_set = FormularioDocumentoSet(initial=inicial)
    id_tramite = int(pk_tramite)
    if request.method == "POST":
        documento_set = FormularioDocumentoSet(request.POST, request.FILES)
        if documento_set.is_valid():
            for docForm in documento_set:
                docForm.save(tramite=tramite)
            if "aceptar_tramite" in request.POST:
                aceptar_inspeccion(request, pk_tramite)
            elif "rechazar_tramite" in request.POST:
                rechazar_inspeccion(request, pk_tramite)
    else:
        return render(request, 'persona/inspector/cargar_inspeccion.html', {'tramite': tramite,
                                                                        'ctxdocumentoset': documento_set,
                                                                        'documentos_requeridos': tipos_de_documentos_requeridos,
                                                                        "perfil": perfil})
    return redirect('inspector')


def aceptar_inspeccion(request, pk_tramite):
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    tramite.hacer(Tramite.APROBAR_INSPECCION, request.user)
    messages.add_message(request, messages.SUCCESS, 'Inspeccion aprobada')
    return redirect('inspector')


def rechazar_inspeccion(request, pk_tramite):
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    tramite.hacer(Tramite.CORREGIR, request.user, request.POST["observaciones"])
    messages.add_message(request, messages.SUCCESS, 'Inspeccion rechazada')
    return redirect('inspector')


def ver_documentos_tramite_inspector(request, pk_estado):
    usuario = request.user
    perfil = 'css/' + usuario.persona.perfilCSS
    estado = get_object_or_404(Estado, pk=pk_estado)
    fecha = estado.timestamp
    fecha_str = datetime.datetime.strftime(fecha, '%d/%m/%Y %H:%M')
    documentos = estado.tramite.documentos.all()
    documentos_fecha = filter(lambda e: (datetime.datetime.strftime(e.fecha, '%d/%m/%Y %H:%M') == fecha_str), documentos)
    contexto = {'documentos_de_fecha': documentos_fecha, "perfil": perfil}
    return render(request, 'persona/inspector/documentos_tramite_inspector.html', contexto)


#def documentos_inspector_estado(request, pk_estado):
#    usuario = request.user
#    perfil = 'css/' + usuario.persona.perfilCSS
#    estado = get_object_or_404(Estado, pk=pk_estado)
#    fecha = estado.timestamp
#    fecha_str = datetime.datetime.strftime(fecha, '%d/%m/%Y %H:%M')
#    documentos = estado.tramite.documentos.all()
#    documentos_fecha = filter(lambda e:(datetime.datetime.strftime(e.fecha, '%d/%m/%Y %H:%M') == fecha_str), documentos)
#    contexto= {'documentos_de_fecha': documentos_fecha, "perfil": perfil}
#    return render(request, 'persona/inspector/documentos_del_estado.html', contexto)


'''jefeinspector ----------------------------------------------------------------------------------------'''


@login_required(login_url="login")
@grupo_requerido('jefeinspector')
def mostrar_jefe_inspector(request):
    usuario = request.user
    perfil = 'css/' + usuario.persona.perfilCSS
    values = {
        "perfil": perfil,
        "ctxtramitesconinspeccion": tramite_con_inspecciones_list(),
        "ctxtramitesagendados": tramites_agendados_por_jefeinspector(request),
        "ctxtramitesinspeccionados": tramites_inspeccionados_por_jefeinspector(request),
        "ctxtramitesinspeccionadosporinspectores": tramites_inspeccionados_por_inspectores(),
        "ctxinspectoresconinspeccionesagendadas": inspecciones_agendadas_por_inspectores()
    }
    for form_name, submit_name in FORMS_JEFEINSPECTOR:
        KlassForm = FORMS_JEFEINSPECTOR[(form_name, submit_name)]
        if request.method == "POST" and submit_name in request.POST:
            _form = KlassForm(request.POST, request.FILES)
            if _form.is_valid():
                _form.save()
                messages.add_message(request, messages.SUCCESS, "La accion solicitada ha sido ejecutada con exito")
                return redirect(usuario.get_view_name())
            else:
                values["submit_name"] = submit_name
                messages.add_message(request, messages.ERROR, "La accion solicitada no a podido ser ejecutada")
            values[form_name] = _form
        else:
            values[form_name] = KlassForm()
    return render(request, 'persona/jefe_inspector/jefe_inspector.html', values)

FORMS_JEFEINSPECTOR = {(k.NAME, k.SUBMIT): k for k in [
    FormularioUsuarioGrupo,
    FormularioUsuarioCambiarDatos,
    FormularioUsuarioContrasenia,
]}


def tramite_con_inspecciones_list():
    argumentos = [FinalObraTotalSolicitado, NoFinalObraTotalSolicitado, CorreccionesDeInspeccionFinalRealizadas]
    tramites = Tramite.objects.en_estado(argumentos)
    contexto = {'tramites': tramites, 'len_tramites': len(tramites)}
    return contexto


def tramites_agendados_por_jefeinspector(request):
    usuario = request.user
    argumentos = [AgendadoInspeccionFinal]
    tramites = Tramite.objects.en_estado(argumentos)
    tramites_del_inspector = filter(lambda t: t.estado().usuario == usuario, tramites)
    dia_hoy = date.today()
    tramites_del_inspector_del_dia = filter(lambda t: datetime.datetime.strftime(t.estado().fecha, '%Y-%m-%d') == datetime.datetime.strftime(dia_hoy, '%Y-%m-%d'), tramites_del_inspector)
    contexto = {'tramites': tramites_del_inspector, 'len_tramites': len(list(tramites_del_inspector_del_dia))}
    return contexto


def tramites_inspeccionados_por_jefeinspector(request):
    usuario = request.user
    estados = Estado.objects.all()
    tipos = [26, 29]
    estados_inspeccionados = filter(lambda estado: (estado.usuario is not None and estado.usuario == usuario and
                                                    (estado.tipo == tipos[0] or estado.tipo == tipos[1])), estados)
    return estados_inspeccionados


def tramites_inspeccionados_por_inspectores():
    estados = Estado.objects.all()
    tipos = [9, 12, 19, 22]
    estados_inspeccionados = filter(lambda estado: (estado.usuario is not None and (estado.tipo == tipos[0] or
                                                                                    estado.tipo == tipos[1] or
                                                                                    estado.tipo == tipos[2] or
                                                                                    estado.tipo == tipos[3])), estados)
    return estados_inspeccionados


def inspectores_sin_inspecciones_agendadas(request, pk_estado):
    usuario = request.user
    perfil = 'css/' + usuario.persona.perfilCSS
    estado = get_object_or_404(Estado, pk=pk_estado)
    usuarios = Usuario.objects.all()
    inspectores = []
    for u in usuarios:
        lista = list(u.groups.values_list('name', flat=True))
        for i in range(len(list(lista))):
            if lista[i] == 'inspector':
                if u not in inspectores:
                    inspectores.append(u)
    estados = Estado.objects.all()
    tipos = [6, 14]
    estados_agendados = filter(lambda e: (e.usuario is not None and (str(e.tramite.estado()) == 'AgendadoPrimerInspeccion' or str(e.tramite.estado()) == 'AgendadoInspeccion') and (e.tipo == tipos[0] or e.tipo == tipos[1])), estados)
    inspectores_estados_agendados = []
    for i in range(len(list(estados_agendados))):
        inspectores_estados_agendados.append(estados_agendados[i].usuario)
    inspectores_sin_insp_agendadas = []
    for inp in inspectores:
        if inp not in inspectores_estados_agendados:
            inspectores_sin_insp_agendadas.append(inp)
    if request.method == "POST" and "cambiar_inspector" in request.POST:
        inspector = get_object_or_404(Usuario, pk=request.POST["idempleado"])
        if estado.usuario.persona.id != inspector.persona.id:
            estado.cambiar_usuario(inspector)
            messages.add_message(request, messages.SUCCESS, "El inspector del tramite ha sido cambiado")
        else:
            messages.add_message(request, messages.ERROR, "El inspector del tramite no ha sido cambiado. Ha seleccionado el mismo inspector")
    else:
        return render(request, 'persona/jefe_inspector/cambiar_inspector_de_inspeccion.html', {'estado': estado, "perfil": perfil, 'inspectores': inspectores_sin_insp_agendadas})
    return redirect('jefe_inspector')


def inspecciones_agendadas_por_inspectores():
    estados = Estado.objects.all()
    tipos = [6, 14]
    estados_agendados= filter(lambda e: (e.usuario is not None and (str(e.tramite.estado()) == 'AgendadoPrimerInspeccion' or str(e.tramite.estado()) == 'AgendadoInspeccion') and (e.tipo == tipos[0] or e.tipo == tipos[1])), estados)
    return estados_agendados


def agendar_inspeccion_final(request, pk_tramite):
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    fecha = parser.parse(request.GET["msg"])
    tramite.hacer(Tramite.AGENDAR_INSPECCION, usuario=request.user, fecha_inspeccion=fecha, inspector=request.user)
    messages.add_message(request, messages.SUCCESS, "La inspeccion final ha sido agendada")
    return redirect('jefe_inspector')


def cargar_inspeccion_final(request, pk_tramite):
    usuario = request.user
    perfil = 'css/' + usuario.persona.perfilCSS
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    tipos_de_documentos_requeridos = TipoDocumento.get_tipos_documentos_para_momento(TipoDocumento.APROBAR_INSPECCION)
    FormularioDocumentoSet = FormularioDocumentoSetFactory(tipos_de_documentos_requeridos)
    inicial = metodo(tipos_de_documentos_requeridos)
    documento_set = FormularioDocumentoSet(initial=inicial)
    id_tramite = int(pk_tramite)
    if request.method == "POST":
        documento_set = FormularioDocumentoSet(request.POST, request.FILES)
        if documento_set.is_valid():
            for docForm in documento_set:
                docForm.save(tramite=tramite)
            if "aceptar_tramite" in request.POST:
                aceptar_inspeccion_final(request, pk_tramite)
            elif "rechazar_tramite" in request.POST:
                rechazar_inspeccion_final(request, pk_tramite)
    else:
        return render(request, 'persona/jefe_inspector/cargar_inspeccion_final.html', {'tramite': tramite,
                                                                            'ctxdocumentoset': documento_set,
                                                                            'documentos_requeridos': tipos_de_documentos_requeridos,
                                                                            "perfil": perfil})
    return redirect('jefe_inspector')


def rechazar_inspeccion_final(request, pk_tramite):
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    tramite.hacer(Tramite.CORREGIR, request.user, request.POST["observaciones"])
    messages.add_message(request, messages.SUCCESS, 'Inspeccion final rechazada')
    return redirect('jefe_inspector')


def aceptar_inspeccion_final(request, pk_tramite):
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    tramite.hacer(Tramite.APROBAR_INSPECCION, request.user)
    messages.add_message(request, messages.SUCCESS, 'Inspeccion final aprobada')
    return redirect('jefe_inspector')


def ver_inspecciones(request, pk_tramite):
    pk = int(pk_tramite)
    estados = Estado.objects.all()
    estados_de_tramite = filter(lambda e: (e.tramite.pk == pk), estados)
    estados = filter(lambda e: (e.tipo == 9), estados_de_tramite)
    usuario = request.user
    perfil = 'css/' + usuario.persona.perfilCSS
    contexto = {'estados': estados, "perfil": perfil}
    return render(request, 'persona/jefe_inspector/vista_de_inspecciones.html', contexto)


def ver_documentos_tramite_jefeinspector(request, pk_estado):
    usuario = request.user
    perfil = 'css/' + usuario.persona.perfilCSS
    estado = get_object_or_404(Estado, pk=pk_estado)
    fecha = estado.timestamp
    fecha_str = datetime.datetime.strftime(fecha, '%d/%m/%Y %H:%M')
    documentos = estado.tramite.documentos.all()
    documentos_fecha = filter(lambda e: (datetime.datetime.strftime(e.fecha, '%d/%m/%Y %H:%M') == fecha_str), documentos)
    contexto = {'documentos_de_fecha': documentos_fecha, "perfil": perfil}
    return render(request, 'persona/jefe_inspector/documentos_tramite_jefeinspector.html', contexto)

def ver_documentos_tramite_inspector_por_jefeinspector(request, pk_estado):
    usuario = request.user
    perfil = 'css/' + usuario.persona.perfilCSS
    estado = get_object_or_404(Estado, pk=pk_estado)
    fecha = estado.timestamp
    fecha_str = datetime.datetime.strftime(fecha, '%d/%m/%Y %H:%M')
    documentos = estado.tramite.documentos.all()
    documentos_fecha = filter(lambda e: (datetime.datetime.strftime(e.fecha, '%d/%m/%Y %H:%M') == fecha_str), documentos)
    contexto = {'documentos_de_fecha': documentos_fecha, "perfil": perfil}
    return render(request, 'persona/jefe_inspector/documentos_tramite_inspector_por_jefeinspector.html', contexto)


'''director ---------------------------------------------------------------------------------------------'''

"""
determina que usuarios pueden o no darse de baja logica segun esten relacionados a algun tramite
"""
def usuarios_no_borrables(usuario):

    #Propietario CONSULTAR: nunca se puede dar de baja. se crea a la par de un tramite asiq siempre esta ligado a un tramite en curso.
    #profesional

    #administrativo
    #director: YO lo dejo. poruqe saca todos los directores menos el de la sesion digamos.
    #visador
    #inspector
    #jefe inspector

    estados = Estado.objects.all()
    setattr(usuario, "relacionado", False)
    setattr(usuario, "descripcion", "")

    try:
        if (usuario.persona.profesional):
            tramites = Tramite.objects.filter(profesional=usuario.persona.profesional.id).values_list('id', flat=True)
            if (len(tramites)>0):
                setattr(usuario, "relacionado", True)
                setattr(usuario, "descripcion", "Profesional asignado a tramite: " + ", ".join([str(id_tramite) for id_tramite in tramites]))

        elif(usuario.persona.propietario):
            tramites = Tramite.objects.filter(propietario=usuario.persona.propietario.id).values_list('id', flat=True)
            if (len(tramites)>0):
                setattr(usuario, "relacionado", True)
                setattr(usuario, "descripcion", "Propietario asignado a tramite: " + ", ".join([str(id_tramite) for id_tramite in tramites]))

        elif (usuario.pertenece_a_grupo('visador')):
            tipo = 7
            estados_agendados = list(filter(lambda e: (e.usuario is not None and str(e.tramite.estado()) == "AgendadoParaVisado" and (e.tipo == tipo)), estados))
            if (any(e.usuario.id == usuario.id for e in estados_agendados)):
                setattr(usuario, "relacionado", True)
                setattr(usuario, "descripcion", "Visador asignado a tramite: " +", ".join([str(e.tramite.id) for e in estados_agendados]))

        elif (usuario.pertenece_a_grupo('inspector')):
            tipos = [6, 14]
            estados_agendados= filter(lambda e: (e.usuario is not None and (str(e.tramite.estado()) == 'AgendadoPrimerInspeccion' or str(e.tramite.estado()) == 'AgendadoInspeccion') and (e.tipo == tipos[0] or e.tipo == tipos[1])), estados)
            if (any(e.usuario.id == usuario.id for e in estados_agendados)):
                setattr(usuario, "relacionado", True)
                setattr(usuario, "descripcion", "Inspector asignado a tramite: " +", ".join([str(e.tramite.id) for e in estados_agendados]))

        elif (usuario.pertenece_a_grupo('jefeinspector')):
            #CHEQUEAR ESTA PARTE VER SI TENGO QUE DARLO DE BAJA O SI TIENE RESTRICCIONES
            setattr(usuario, "relacionado", True)
            setattr(usuario, "descripcion", "Jefe Inspector asignado a un tramite en curso")

    except Exception as e: #Puede originarse por usuarios sin persona
        pass
    return usuario


@login_required(login_url="login")
@grupo_requerido('director')
def mostrar_director(request):
    usuario = request.user
    lista_usuarios = map(usuarios_no_borrables, Usuario.objects.all().exclude(id=request.user.id))
    perfil = 'css/' + usuario.persona.perfilCSS
    tipos_de_documento = TipoDocumento.objects.all()
    print(tipos_de_documento)
    values = {
        "lista_usuarios": lista_usuarios,
        "perfil": perfil,
        "datos_usuario": empleados(request.user),
        "tipos_de_documento" : tipos_de_documento,
        "ctxvisadorescontramitesagendados": []#tramites_con_visado_agendado(),
    }
    for form_name, submit_name in FORMS_DIRECTOR:
        KlassForm = FORMS_DIRECTOR[(form_name, submit_name)]
        if request.method == "POST" and submit_name in request.POST:
            _form = KlassForm(request.POST, request.FILES)
            if _form.is_valid():
                _form.save()
                messages.add_message(request, messages.SUCCESS, "La accion solicitada ha sido ejecutada con exito")
                return redirect(usuario.get_view_name())
            else:
                values["submit_name"] = submit_name
                messages.add_message(request, messages.ERROR, "La accion solicitada no a podido ser ejecutada")
            values[form_name] = _form
        else:
            values[form_name] = KlassForm()
    return render(request, 'persona/director/director.html', values)

FORMS_DIRECTOR = {(k.NAME, k.SUBMIT): k for k in [
    FormularioTipoDocumento,
    FormularioUsuarioPersona,  #este formulario no se necesitaria, solo se dan de alta visador, inspector y administrativo
    FormularioTipoObra,
    FormularioTipoDocumento,
    FormularioUsuarioGrupo,
    FormularioUsuarioCambiarDatos,
    FormularioUsuarioContrasenia,
]}


def empleados(director):
    usuarios = Usuario.objects.all().exclude(id=director.id)
    empleados = []
    for u in usuarios:
        lista = list(u.groups.values_list('name', flat=True))
        for i in range(len(lista)):
            if lista[i] != 'profesional' and lista[i] != 'propietario':
                if u not in empleados:
                    empleados.append(u)
    return empleados


def tramites_con_visado_agendado():
    estados = Estado.objects.all()
    tipos = [7]
    estados_agendados= filter(lambda e: (e.usuario is not None and str(e.tramite.estado()) == 'AgendadoParaVisado' and e.tipo == tipos[0]), estados)
    return estados_agendados


def visadores_sin_visado_agendado(request, pk_estado):
    usuario = request.user
    perfil = 'css/' + usuario.persona.perfilCSS
    estado = get_object_or_404(Estado, pk=pk_estado)
    usuarios = Usuario.objects.all()
    visadores = []
    for u in usuarios:
        lista = list(u.groups.values_list('name', flat=True))
        for i in range(len(lista)):
            if lista[i] == 'visador':
                if u not in visadores:
                    visadores.append(u)
    estados = Estado.objects.all()
    tipo = 7
    estados_agendados = filter(lambda e: (e.usuario is not None and str(e.tramite.estado()) == 'AgendadoParaVisado' and e.tipo == tipo), estados)
    visadores_estados_agendados = []
    for i in range(len(list(estados_agendados))):
        visadores_estados_agendados.append(estados_agendados[i].usuario)
    visadores_sin_vis_agendadas = []
    for vis in visadores:
        if vis not in visadores_estados_agendados:
            visadores_sin_vis_agendadas.append(vis)
    if request.method == "POST" and "cambiar_visador" in request.POST:
        visador = get_object_or_404(Usuario, pk=request.POST["idempleado"])
        if estado.usuario.persona.id != visador.persona.id:
            estado.cambiar_usuario(visador)
            messages.add_message(request, messages.SUCCESS, "El visador del tramite ha sido cambiado")
        else:
            messages.add_message(request, messages.ERROR, "El visador del tramite no ha sido cambiado. Ha seleccionado el mismo inspector")
    else:
        return render(request, 'persona/director/cambiar_visador_de_tramite.html', {'estado': estado, "perfil": perfil, 'visadores': visadores_sin_vis_agendadas})
    return redirect('director')


def ver_listado_todos_tramites(request):
    usuario = request.user
    perfil = 'css/' + usuario.persona.perfilCSS
    argumentos = [Iniciado, Aceptado, AgendadoParaVisado, Visado, AgendadoPrimerInspeccion, PrimerInspeccion,
              AprobadoSolicitado, Aprobado, NoAprobadoSolicitado, NoAprobado, AprobadoSolicitadoPorPropietario,
              AprobadoPorPropietario]
    argumentos2 = [AgendadoInspeccion, Inspeccionado, FinalObraTotalSolicitado,
              FinalObraParcialSolicitado, NoFinalObraTotalSolicitado, AgendadoInspeccionFinal, InspeccionFinal,
              Finalizado, NoFinalizado, FinalObraTotalSolicitadoPorPropietario, Baja]
    lab = ['Iniciado', 'Aceptado', 'A.Visado', 'Visado', 'A.Inspeccion', 'Inspeccion', 'A.Solicitado', 'Aprobado',
           'N.A.Solicitado', 'NoAprobado', 'A.S.x Propietario', 'A.x Propietario']
    lab2 = ['A.Inspeccion', 'Inspeccionado', 'F.O.T.S.', 'F.O.P.S.', 'NoF.O.T.S.', 'A.InspeccionFinal', 'InspeccionFinal',
                   'Finalizado', 'NoFinalizado', 'F.O.T.S.x Prop.', 'Baja']
    len_argumentos = len(argumentos)
    tramites = Tramite.objects.en_estado(argumentos)
    estados = []
    for t in tramites:
        estados.append(t.estado().tipo)
    print("----------------------------")
    print(estados)
    print("----------------------------")
    estados_cant = dict(collections.Counter(estados))
    print(estados_cant)
    print("----------------------------")
    for n in range(1, (len_argumentos+1)):
        if (not estados_cant.has_key(n)):
            estados_cant.setdefault(n, 0)
    estados_datos = estados_cant.values()
    print(estados_datos)
    print("----------------------------")
    contexto = {'todos_los_tramites': tramites, "datos_estados":estados_datos, "label_estados":lab, "perfil" : perfil}
    return render(request, 'persona/director/vista_de_tramites.html', contexto)

def ver_listado_todos_usuarios(request):
    grupos = Group.objects.all()
    label_grupos = []
    for g in grupos:
        if g.name != 'profesional' and g.name != 'propietario':
            label_grupos.append(g.name)
    usuarios = Usuario.objects.all()
    cant_usuarios_grupos = []
    for u in usuarios:
        for gu in u.get_view_groups():
            if str(gu) != 'profesional' and str(gu) != 'propietario':
                cant_usuarios_grupos.append(gu)
    total_usuarios_grupos = dict(collections.Counter(cant_usuarios_grupos))
    for lg in label_grupos:
        if not total_usuarios_grupos.has_key(lg):
            total_usuarios_grupos.setdefault(lg, 0)
    datos_grupos = total_usuarios_grupos.values()
    usuario = request.user
    perfil = 'css/' + usuario.persona.perfilCSS
    return render(request, 'persona/director/vista_de_usuarios.html', {'todos_los_usuarios': usuarios, "label_grupos": label_grupos, "datos_grupos": datos_grupos,  "perfil": perfil})


def ver_actividad_usuario(request, usuario):
    usuarios = Usuario.objects.all()
    usuario_req = filter(lambda u: (str(u) == usuario), usuarios)
    estados = Estado.objects.all()
    estados_usuario_req = filter(lambda estado:(str(estado.usuario) == str(usuario_req[0])), estados)
    fechas_del_estado = []
    estados_por_fecha = []
    for e in estados_usuario_req:
        estados_por_fecha.append(e.timestamp.strftime("%d/%m/%Y"))
        if (e.timestamp.strftime("%d/%m/%Y")) not in fechas_del_estado:
            fechas_del_estado.append(e.timestamp.strftime("%d/%m/%Y"))
    cant_estados_por_fecha = [estados_por_fecha.count(f) for f in fechas_del_estado]
    user = request.user
    perfil = 'css/' + user.persona.perfilCSS
    return render(request, 'persona/director/vista_de_actividad_usuario.html', {"perfil": perfil,
                                                                                "usuario": usuario_req[0],
                                                                                "estados": estados_usuario_req,
                                                                                "fechas_estados": fechas_del_estado,
                                                                                "cant_estados": cant_estados_por_fecha})


def detalle_de_tramite(request, pk_tramite):
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    contexto0 = {'tramite': tramite}
    pk = int(pk_tramite)
    estados = Estado.objects.all()
    estados_de_tramite = filter(lambda e: (e.tramite.pk == pk), estados)
    contexto1 = {'estados_del_tramite': estados_de_tramite}
    fechas_del_estado = []
    for est in estados_de_tramite:
        fechas_del_estado.append(est.timestamp.strftime("%d/%m/%Y"))
    usuario = request.user
    perfil = 'css/' + usuario.persona.perfilCSS
    return render(request, 'persona/director/detalle_de_tramite.html', {"tramite": contexto0, "estados": contexto1, "fecha": fechas_del_estado, "perfil": perfil})


def ver_documentos_del_estado(request, pk_estado):
    usuario = request.user
    perfil = 'css/' + usuario.persona.perfilCSS
    estado = get_object_or_404(Estado, pk=pk_estado)
    fecha = estado.timestamp
    fecha_str = datetime.datetime.strftime(fecha, '%d/%m/%Y %H:%M')
    documentos = estado.tramite.documentos.all()
    documentos_fecha = filter(lambda e:(datetime.datetime.strftime(e.fecha, '%d/%m/%Y %H:%M') == fecha_str), documentos)
    contexto= {'documentos_de_fecha': documentos_fecha, "perfil": perfil}
    return render(request, 'persona/director/ver_documentos_del_estado.html', contexto)


class ReporteTramitesDirectorExcel(TemplateView):

    def get(self, request, *args, **kwargs):
        tramites = Tramite.objects.all()
        wb = Workbook()
        ws = wb.active
        ws['A1'] = 'REPORTE DE TRAMITES'
        ws.merge_cells('B1:G1')
        ws['B2'] = 'NRO'
        ws['C2'] = 'TIPO_DE_OBRA'
        ws['D2'] = 'PROFESIONAL'
        ws['E2'] = 'PROPIETARIO'
        ws['F2'] = 'MEDIDAS'
        cont = 3
        for tramite in tramites:
            ws.cell(row=cont, column=2).value = tramite.id
            ws.cell(row=cont, column=3).value = str(tramite.tipo_obra)
            ws.cell(row=cont, column=4).value = str(tramite.profesional)
            ws.cell(row=cont, column=5).value = str(tramite.propietario)
            ws.cell(row=cont, column=6).value = tramite.medidas
            cont = cont + 1
        nombre_archivo = "ReportePersonasExcel.xlsx"
        response = HttpResponse(content_type="application/ms-excel")
        contenido = "attachment; filename={0}".format(nombre_archivo)
        response["Content-Disposition"] = contenido
        wb.save(response)
        return response


class ReporteTramitesDirectorPdf(View):

    def get(self, request, *args, **kwargs):
        filename = "Informe de tramites.pdf"
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="%s"' % filename
        doc = SimpleDocTemplate(
            response,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=15,
            bottomMargin=28,
        )
        story = []
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='Usuario', alignment=TA_RIGHT, fontName='Helvetica', fontSize=8))
        styles.add(ParagraphStyle(name='Titulo', alignment=TA_RIGHT, fontName='Helvetica', fontSize=18))
        styles.add(ParagraphStyle(name='Subtitulo', alignment=TA_RIGHT, fontName='Helvetica', fontSize=12))
        usuario = 'Usuario: ' + request.user.username + ' -  Fecha:' + ' ... aca va la fecha'
        story.append(Paragraph(usuario, styles["Usuario"]))
        story.append(Spacer(0, cm * 0.15))
        im0 = Image(settings.MEDIA_ROOT + '/imagenes/espacioPDF.png', width=490, height=3)
        im0.hAlign = 'CENTER'
        story.append(im0)
        titulo = 'SISTEMA OBRAS PARTICULARES'
        story.append(Paragraph(titulo, styles["Titulo"]))
        story.append(Spacer(0, cm * 0.20))
        subtitulo = 'Reporte de tramites'
        story.append(Paragraph(subtitulo, styles["Subtitulo"]))
        story.append(Spacer(0, cm * 0.15))
        story.append(im0)
        story.append(Spacer(0, cm * 0.5))
        encabezados = ('NRO', 'TIPO_DE_OBRA', 'PROFESIONAL', 'PROPIETARIO', 'MEDIDAS', 'ESTADO')
        detalles = [
            (tramite.id, tramite.tipo_obra, tramite.profesional, tramite.propietario, tramite.medidas, tramite.estado())
            for tramite in
            Tramite.objects.all()]
        detalle_orden = Table([encabezados] + detalles, colWidths=[1 * cm, 3 * cm, 4 * cm, 4 * cm, 2 * cm, 3 * cm])
        detalle_orden.setStyle(TableStyle(
            [
                ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 1, colors.gray),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('LINEBELOW', (0, 0), (-1, 0), 2, colors.darkblue),
                ('BACKGROUND', (0, 0), (-1, 0), colors.dodgerblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ]
        ))
        detalle_orden.hAlign = 'CENTER'
        story.append(detalle_orden)
        doc.build(story)
        return response

class ReporteEmpleadosDirectorExcel(TemplateView):

    def get(self, request, *args, **kwargs):
        empleados = Usuario.objects.all()
        wb = Workbook()
        ws = wb.active
        ws['A1'] = 'REPORTE DE TRAMITES'
        ws.merge_cells('B1:G1')
        ws['B2'] = 'NRO'
        ws['C2'] = 'TIPO_DE_OBRA'
        ws['D2'] = 'PROFESIONAL'
        ws['E2'] = 'PROPIETARIO'
        ws['F2'] = 'MEDIDAS'
        cont = 3
        '''
        for tramite in tramites:
            ws.cell(row=cont, column=2).value = Usuario.id
            ws.cell(row=cont, column=3).value = str(tramite.tipo_obra)
            ws.cell(row=cont, column=4).value = str(tramite.profesional)
            ws.cell(row=cont, column=5).value = str(tramite.propietario)
            ws.cell(row=cont, column=6).value = tramite.medidas
            cont = cont + 1
        '''
        nombre_archivo = "ReporteEmpleadosExcel.xlsx"
        response = HttpResponse(content_type="application/ms-excel")
        contenido = "attachment; filename={0}".format(nombre_archivo)
        response["Content-Disposition"] = contenido
        wb.save(response)
        return response



class RotarImagen(Image):
    def wrap(self, availWidth, availHeight):
        self.w, self.h = Image.wrap(self, availWidth, availHeight)
        return self.w, self.h

    def draw(self):
        self.canv.translate(0,self.h)
        self.canv.rotate(-90)
        Image.draw(self)

class ReporteEmpleadosDirectorPdf(View):

    def get(self, request, *args, **kwargs):
        filename = "Informe de empleados.pdf"
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="%s"' % filename
        doc = SimpleDocTemplate(
            response,
            pagesize=letter,
            rightMargin=0,
            leftMargin=0,
            topMargin=0,
            bottomMargin=0,
        )

        story = []
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='Usuario', alignment=TA_RIGHT, fontName='Helvetica', fontSize=10))
        styles.add(ParagraphStyle(name='Subtitulo', alignment=TA_RIGHT, fontName='Helvetica', fontSize=12))

        usuario = 'Usuario: ' + str(request.user.persona) + ' -  Fecha: ' + datetime.datetime.now().strftime("%Y/%m/%d")
        story.append(Paragraph(usuario, styles["Usuario"]))
        story.append(Spacer(0, cm * 0.15))

        im1 = Image(settings.MEDIA_ROOT + '/imagenes/banner_municipio_3.png', width=630, height=50)
        im1.hAlign = 'CENTER'
        story.append(im1)

        story.append(Spacer(0, cm * 0.05))
        subtitulo = 'Reporte de empleados'
        story.append(Paragraph(subtitulo, styles["Subtitulo"]))
        story.append(Spacer(0, cm * 0.15))

        im0 = Image(settings.MEDIA_ROOT + '/imagenes/espacioPDF.png', width=640, height=3)
        story.append(im0)
        story.append(Spacer(0, cm * 0.5))

        encabezados = ('NRO', 'TIPO_DE_OBRA', 'PROFESIONAL', 'PROPIETARIO', 'MEDIDAS', 'ESTADO')
        detalles = []
        '''
        detalles = [
            (tramite.id, tramite.tipo_obra, tramite.profesional, tramite.propietario, tramite.medidas, tramite.estado())
            for tramite in
            Tramite.objects.all()]
        '''
        detalle_orden = Table([encabezados] + detalles, colWidths=[1 * cm, 3 * cm, 4 * cm, 4 * cm, 2 * cm, 3 * cm])
        detalle_orden.setStyle(TableStyle(
            [
                ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 1, colors.gray),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('LINEBELOW', (0, 0), (-1, 0), 2, colors.darkblue),
                ('BACKGROUND', (0, 0), (-1, 0), colors.dodgerblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ]
        ))
        detalle_orden.hAlign = 'CENTER'
        story.append(detalle_orden)

        '''
        trabajando con los graficos dentro del informe
        '''
        d = Drawing(500, 200)
        data = [
            (13, 5, 20, 22, 37, 45, 19, 4),
            (14, 6, 21, 23, 38, 46, 20, 5)
        ]
        bc = VerticalBarChart()
        bc.x = 50
        bc.y = 50
        bc.height = 125
        bc.width = 500
        bc.data = data
        bc.strokeColor = colors.black
        bc.valueAxis.valueMin = 0
        bc.valueAxis.valueMax = 50
        bc.valueAxis.valueStep = 10  # paso de distancia entre punto y punto
        bc.categoryAxis.labels.boxAnchor = 'ne'
        bc.categoryAxis.labels.dx = 8
        bc.categoryAxis.labels.dy = -2
        bc.categoryAxis.labels.angle = 30
        bc.categoryAxis.categoryNames = ['Ene-14', 'Feb-14', 'Mar-14',
                                         'Abr-14', 'May-14', 'Jun-14', 'Jul-14', 'Ago-14']
        bc.groupSpacing = 10
        bc.barSpacing = 2
        d.add(bc)
        story.append(d)

        '''
        hasta aca, anda pero ver los valores, colores y como se ubica dentro de pagina
        '''

        doc.build(story)
        return response


'''general ----------------------------------------------------------------------------------------------'''

def cambiar_perfil(request):
    usuario = request.user
    if request.method == "POST":
        estilo = request.POST["estiloCSS"]
        usuario.persona.modificarPerfilCSS(estilo)
        return redirect(usuario.get_view_name())


'''Funcionalidades 2018 pre-final -----------------------------------------------------------------------'''

def alta_persona(request):
    if request.method == "POST":
        form = FormularioPersona(request.POST)
        if form.is_valid():
            persona = form.save()
            persona.save()
    else:
        form = FormularioPersona()
    return render(request, 'persona/alta/alta_persona.html', {'form': form})


"""
Metodo que se encarga de realizar el alta baja de los usuarios
Se utiliza en la vista de director
"""
@login_required(login_url="login")
@grupo_requerido('director')
def alta_baja_usuarios(request):
    if request.method == 'POST':
        id_usuario = request.POST.get('id_form_usuario')
        opcion = request.POST.get('id_form_opcion')
        usuario = Usuario.objects.get(id=int(id_usuario))
        if (opcion == 'Baja'):
            usuario.is_active = False
        else:
            usuario.is_active = True
        usuario.save()
    return redirect('director')


"""
Metodo que se encarga de devolver los grupos a los que pertenece un usuario
Se utiliza en la vista de director
"""
@login_required(login_url="login")
@grupo_requerido('director')
def get_grupos_usuario(request):
    if request.is_ajax():
        id = request.GET.get('usuario_id')
        lista = Usuario.objects.filter(id=int(id)).values_list('groups__name',flat=True)
        return JsonResponse(list(lista), safe=False)

"""
Metodo que se encarga de devolver todos los profesionales que tienen un usuario
Se utiliza en la vista de administrativo
"""
@login_required(login_url="login")
@grupo_requerido('administrativo')
def listado_profesionales_administrativo(request):
    usuario = request.user
    perfil = 'css/' + usuario.persona.perfilCSS
    personas = Persona.objects.all()
    profesionales_con_usuario = filter(lambda persona: (persona.usuario is not None and persona.profesional is not None), personas)
    contexto = {'profesionales': profesionales_con_usuario, "perfil": perfil}
    return render(request, 'persona/profesional/profesional_list_con_usuario_administrativo.html', contexto)


"""
Metodo que se encarga de devolver todos los propietarios con usuario
Se utiliza en la vista de administrativo
"""
@login_required(login_url="login")
@grupo_requerido('administrativo')
def listado_propietarios_administrativo(request):
    usuario = request.user
    perfil = 'css/' + usuario.persona.perfilCSS
    propietarios = Propietario.objects.all()
    propietarios_con_usuario = filter(lambda propietario: (propietario.persona.usuario is not None and propietario.persona is not None ), propietarios)
    contexto = {'propietarios': propietarios_con_usuario, "perfil": perfil}
    return render(request, 'persona/propietario/propietario_list_con_usuario_administrativo.html', contexto)


"""
Metodo que se encarga de devolver todos los profesionales con usuario
Se utiliza en la vista de director
"""
@login_required(login_url="login")
@grupo_requerido('director')
def listado_profesionales_director(request):
    usuario = request.user
    perfil = 'css/' + usuario.persona.perfilCSS
    personas = Persona.objects.all()
    profesionales_con_usuario = filter(lambda persona: (persona.usuario is not None and persona.profesional is not None), personas)
    contexto = {'profesionales': profesionales_con_usuario, "perfil": perfil}
    return render(request, 'persona/profesional/profesional_list_con_usuario_director.html', contexto)


"""
Metodo que se encarga de devolver todos los propietarios con usuario
Se utiliza en la vista de director
"""
@login_required(login_url="login")
@grupo_requerido('director')
def listado_propietarios_director(request):
    usuario = request.user
    perfil = 'css/' + usuario.persona.perfilCSS
    propietarios = Propietario.objects.all()
    propietarios_con_usuario = filter(lambda propietario: (propietario.persona.usuario is not None and propietario.persona is not None ), propietarios)
    contexto = {'propietarios': propietarios_con_usuario, "perfil": perfil}
    return render(request, 'persona/propietario/propietario_list_con_usuario_director.html', contexto)
