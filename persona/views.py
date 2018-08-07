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
from django.views.generic.detail import DetailView
import re
from datetime import datetime, date, time, timedelta
from django.views.generic.base import TemplateView
from openpyxl import Workbook
from django.http.response import HttpResponse
from django.views.generic import View
from django.conf import settings
from io import BytesIO

from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, TableStyle, Table, Image, Spacer
from reportlab.lib import colors
from reportlab.lib.units import cm, inch
from reportlab.lib.pagesizes import letter, A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
import time
from datetime import datetime
import collections

from reportlab.graphics.shapes import Drawing, String
from reportlab.graphics import renderPDF
from reportlab.graphics.charts.barcharts import VerticalBarChart


'''
generales -----------------------------------------------------------------------------------------------------
'''

DATETIME = re.compile("^(\d{4})\-(\d{2})\-(\d{2})\s(\d{1,2}):(\d{2})$")

def convertidor_de_fechas(fecha):
    return datetime(*[int(n) for n in DATETIME.match(fecha).groups()])

'''
propietario ---------------------------------------------------------------------------------------------------
'''


@login_required(login_url="login")
@grupo_requerido('propietario')
def mostrar_propietario(request):
    usuario = request.user
    perfil = 'css/' + usuario.persona.perfilCSS
    values = {
        "perfil": perfil,
        "ctxtramitespropietario": listado_tramites_propietario(request)
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
    tramites = Tramite.objects.all()
    personas = Persona.objects.all()
    usuario = request.user
    lista_de_persona_que_esta_logueada = filter(lambda persona: (persona.usuario is not None and persona.usuario == usuario), personas)
    persona = list(lista_de_persona_que_esta_logueada).pop()
    propietario = persona.get_propietario()
    tramites_de_propietario = filter(lambda tramite: (tramite.propietario == propietario), tramites)
    return tramites_de_propietario


def propietario_solicita_final_obra(request, pk_tramite):
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    try:
        tramite.hacer(Tramite.SOLICITAR_FINAL_OBRA, request.user)
        messages.add_message(request, messages.SUCCESS, 'final de obra solicitado.')
    except:
        messages.add_message(request, messages.ERROR, 'No puede solicitar el final de obra para ese tramite.')
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
    fecha_str = datetime.strftime(fecha, '%d/%m/%Y %H:%M')
    documentos = estado.tramite.documentos.all()
    documentos_fecha = filter(lambda e:(datetime.strftime(e.fecha, '%d/%m/%Y %H:%M') == fecha_str), documentos)
    contexto= {'documentos_de_fecha': documentos_fecha, "perfil": perfil}
    return render(request, 'persona/propietario/documentos_de_estado.html', contexto)


'''
profesional ----------------------------------------------------------------------------------------------------
'''


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
        if int(usuario.persona.profesional.categoria) >= int(request.POST['tipo_obra']) and len(list(t)) == 0:
            personas = Persona.objects.filter(dni=request.POST["propietario"])
            persona = personas.exists() and personas.first() or None
            documento_set = FormularioDocumentoSet(request.POST, request.FILES)
            propietario_form = FormularioPropietario(request.POST)
            tramite_form = FormularioIniciarTramite(request.POST)
            documento_set = FormularioDocumentoSet(request.POST, request.FILES)
            propietario = propietario_form.obtener_o_crear(persona)
            if propietario is not None and tramite_form.is_valid() and documento_set.is_valid():
                tramite = tramite_form.save(propietario=propietario, commit=False)
                lista=[]
                for docForm in documento_set:
                   lista.append(docForm.save(commit=False))
                Tramite.new(usuario, propietario, usuario.persona.profesional,request.POST['tipo_obra'],request.POST['medidas'],request.POST['domicilio'],lista, request.POST['destino_obra'])
                tramite_form = FormularioIniciarTramite(initial={'profesional':usuario.persona.profesional.pk})
                propietario_form = None
                messages.add_message(request, messages.SUCCESS,'Solicitud de iniciar tramitre reallizada con exito.')
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
    contexto = {'tramites_de_profesional': tramites_de_profesional}
    return contexto


def tramites_corregidos(request):
    tramites = Tramite.objects.all()
    personas = Persona.objects.all()
    usuario = request.user
    lista_de_persona_que_esta_logueada = filter(lambda persona: (persona.usuario is not None and persona.usuario == usuario), personas)
    persona = list(lista_de_persona_que_esta_logueada).pop()
    profesional = persona.get_profesional()
    tramites_de_profesional = filter(lambda tramite: (tramite.profesional == profesional), tramites)
    tipo = 4
    tram_corregidos = filter(lambda tramite: (tramite.estado().tipo == tipo), tramites_de_profesional)
    contexto = {'tramites': tram_corregidos}
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
                                                                            "fecha":fechas_del_estado,                                                                         "perfil": perfil})
def profesional_solicita_aprobar_tramite(request, pk_tramite):
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    try:
        tramite.hacer(Tramite.SOLICITAR_APROBAR_TRAMITE, request.user)
        messages.add_message(request, messages.SUCCESS, 'Solicitud de aprobar tramite realizada.')
    except:
        messages.add_message(request, messages.ERROR, 'No puede solicitar aprobar tramite para ese tramite.')
    finally:
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


def profesional_solicita_final_obra(request, pk_tramite):
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    try:
        tramite.hacer(Tramite.SOLICITAR_FINAL_OBRA_TOTAL, request.user)
        messages.add_message(request, messages.SUCCESS, 'final de obra solicitado.')
    except:
        messages.add_message(request, messages.ERROR, 'No puede solicitar el final de obra para ese tramite.')
    finally:
        return redirect('profesional')


def ver_documentos_corregidos(request, pk_tramite):
    usuario = request.user
    perfil = 'css/' + usuario.persona.perfilCSS
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    if request.method == "POST":
        enviar_correcciones(request, pk_tramite)
    else:
        return render(request, 'persona/profesional/ver_documentos_corregidos.html', {'tramite': tramite,
                                                                                      "perfil": perfil})
    return redirect('profesional')


def enviar_correcciones(request, pk_tramite):
    usuario = request.user
    observacion = "Este tramite ya tiene los archivos corregidos cargados"
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    tramite.hacer(tramite.CORREGIR, request.user, observacion)
    messages.add_message(request, messages.SUCCESS, 'Tramite con documentos corregidos y enviados')
    return redirect('profesional')


def documento_de_estado(request, pk_estado):
    usuario = request.user
    perfil = 'css/' + usuario.persona.perfilCSS
    estado = get_object_or_404(Estado, pk=pk_estado)
    fecha = estado.timestamp
    fecha_str = datetime.strftime(fecha, '%d/%m/%Y %H:%M')
    documentos = estado.tramite.documentos.all()
    documentos_fecha = filter(lambda e:(datetime.strftime(e.fecha, '%d/%m/%Y %H:%M') == fecha_str), documentos)
    contexto= {'documentos_de_fecha': documentos_fecha, "perfil": perfil}
    return render(request, 'persona/profesional/documento_de_estado.html', contexto)


'''
administrativo ------------------------------------------------------------------------------------------------
'''


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
        #"ctxtramitesvencidos": listado_tramites_vencidos()
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
    contexto = {'personas': profesionales}
    return contexto


def propietario_list():
    propietarios = Propietario.objects.all()
    propietarios_sin_usuario = filter(lambda propietario: (propietario.persona.usuario is None and propietario.persona is not None ), propietarios)
    contexto = {'propietarios': propietarios_sin_usuario}
    return contexto


def listado_de_tramites_iniciados():
    tramites = Tramite.objects.en_estado(Iniciado)
    contexto = {'tramites': tramites}
    return contexto


def tramite_corregidos_list():
    tramites = Tramite.objects.all()
    contexto = {'tramites': tramites}
    return contexto


def solicitud_final_obra_list():
    tramites = Tramite.objects.en_estado(FinalObraTotalSolicitado)
    contexto = {'tramites': tramites}
    return contexto

def solicitud_aprobacion_list():
    tramites = Tramite.objects.en_estado(AprobadoSolicitado)
    contexto = {'tramites': tramites}
    return contexto

def solicitud_no_aprobacion_list():
    tramites = Tramite.objects.en_estado(NoAprobadoSolicitado)
    contexto = {'tramites': tramites}
    return contexto

def listado_tramites_pago_vencido():
    #argumentos = [Iniciado, Aceptado, Visado, Corregido, AgendadoInspeccion, ConInspeccion]
    #tramites = Tramite.objects.en_estado(argumentos)
    tramites = Tramite.objects.all()
    contexto = {'tramites': tramites}
    print (contexto)
    return contexto


def listado_tramites_plazo_vencido():
    #argumentos = [Corregido, AgendadoInspeccion, ConInspeccion]
    #tramites = Tramite.objects.en_estado(argumentos)
    tramites = Tramite.objects.all()
    contexto = {'tramites': tramites}
    print (contexto)
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


def habilitar_final_obra(request, pk_tramite):
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    try:
        tramite.hacer(tramite.AGENDAR_INSPECCION, request.user)
        messages.add_message(request, messages.SUCCESS, 'final de obra habilitado.')
    except:
        messages.add_message(request, messages.ERROR, 'No puede otorgar final de obra total para ese tramite.')
    finally:
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
    tramite.hacer(tramite.RECHAZAR, request.user, request.GET["msg"])
    messages.add_message(request, messages.WARNING, 'Tramite rechazado.')
    return redirect('administrativo')


class ver_un_certificado(DetailView):
    model = Persona
    template_name = 'persona/administrativo/ver_certificado_profesional.html'
    def dispatch(self, *args, **kwargs):
        return super(ver_un_certificado, self).dispatch(*args, **kwargs)


def ver_documentos_tramite_administrativo(request, pk_tramite):
    usuario = request.user
    perfil = 'css/' + usuario.persona.perfilCSS
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    return render(request, 'persona/administrativo/vista_de_documentos_administrativo.html', {'tramite': tramite,
                                                                                              "perfil": perfil})


'''
visador ----------------------------------------------------------------------------------------------------------
'''


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
    argumentos = [Aceptado] #falta conCorreccionesVisado
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
    contexto = {'tramites': tramites_del_visador}
    return contexto


def tramites_visados(request):
    usuario = request.user
    estados = Estado.objects.all()
    tipo = 4
    estados_visado = filter(lambda estado: (estado.usuario is not None and estado.usuario == usuario and estado.tipo == tipo), estados)
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
        tramites = Tramite.objects.all()
        tramite = filter(lambda t: str(t.pk) == str(tram), tramites)
        monto_permiso = tramite[0].medidas * tramite[0].tipo_obra.valor_de_superficie
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


def ver_documentos_visados(request, pk_tramite):
    usuario = request.user
    perfil = 'css/' + usuario.persona.perfilCSS
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    return render(request, 'persona/visador/ver_documentos_visados.html', {'tramite': tramite, "perfil": perfil})


def aprobar_visado(request, pk_tramite, monto):
    usuario = request.user
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    tramite.hacer(tramite.VISAR, usuario)
    tramite.monto_a_pagar= monto
    tramite.save()
    messages.add_message(request, messages.SUCCESS, 'Tramite visado aprobado')
    return redirect('visador')


def no_aprobar_visado(request, pk_tramite, observacion):
    usuario = request.user
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    obs = observacion
    tramite.hacer(tramite.CORREGIR, usuario, obs)
    messages.add_message(request, messages.SUCCESS, 'Tramite con visado no aprobado')
    return redirect('visador')


class ReporteTramitesAceptadosExcel(TemplateView):

    def get(self, request, *args, **kwargs):
        tramites = Tramite.objects.en_estado(Aceptado)
        wb = Workbook()
        ws = wb.active
        ws['B1'] = 'REPORTE DE TRAMITES ACEPTADOS'
        ws.merge_cells('B1:F1')
        ws['C2'] = 'TIPO_DE_OBRA'
        ws['D2'] = 'PROFESIONAL'
        ws['E2'] = 'PROPIETARIO'
        ws['F2'] = 'MEDIDAS'
        cont = 3
        for tramite in tramites:
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


class ReporteTramitesAceptadosPdf(View):

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
        subtitulo = 'Reporte De Tramites Iniciados para visar'
        story.append(Paragraph(subtitulo, styles["Subtitulo"]))
        story.append(Spacer(0, cm * 0.15))
        story.append(im0)
        story.append(Spacer(0, cm * 0.5))
        encabezados = ('TIPO DE OBRA', 'PROFESIONAL', 'PROPIETARIO', 'MEDIDAS', 'ESTADO')
        detalles = [(tramite.tipo_obra, tramite.profesional, tramite.propietario, tramite.medidas, tramite.estado()) for
                    tramite in
                    Tramite.objects.en_estado(Aceptado)]
        detalle_orden = Table([encabezados] + detalles, colWidths=[4 * cm, 4 * cm, 4 * cm, 3 * cm, 2 * cm])
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


'''
inspector ------------------------------------------------------------------------------------------------------
'''


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
    argumentos = [Visado, Inspeccionado, Aprobado] #falta conCorreccionesInspeccion
    tramites = Tramite.objects.en_estado(argumentos)
    return tramites


def tramites_inspeccionados_por_inspector(request):
    usuario = request.user
    estados = Estado.objects.all()
    tipo = 7
    '''aca no es solo tipo 7'''
    estados_inspeccionados = filter(lambda estado: (estado.usuario is not None and estado.usuario == usuario and
                                                    estado.tipo == tipo), estados)
    return estados_inspeccionados


def tramites_agendados_por_inspector(request):
    usuario = request.user
    argumentos = [AgendadoPrimerInspeccion, AgendadoInspeccion]
    tramites = Tramite.objects.en_estado(argumentos)
    tramites_del_inspector = filter(lambda t: t.estado().usuario == usuario, tramites)
    return tramites_del_inspector


def agendar_tramite(request, pk_tramite):
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    fecha = convertidor_de_fechas(request.GET["msg"])
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


def rechazar_inspeccion(request, pk_tramite):
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    tramite.hacer(Tramite.CORREGIR, request.user, request.POST["observaciones"])
    messages.add_message(request, messages.ERROR, 'Inspeccion rechazada')
    return redirect('inspector')


def aceptar_inspeccion(request, pk_tramite):
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    tramite.hacer(Tramite.APROBAR_INSPECCION, request.user)
    messages.add_message(request, messages.SUCCESS, 'Inspeccion aprobada')
    return redirect('inspector')


def ver_documentos_tramite_inspector(request, pk_tramite):
    usuario = request.user
    perfil = 'css/' + usuario.persona.perfilCSS
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    return render(request, 'persona/inspector/documentos_tramite_inspector.html', {'tramite': tramite, "perfil": perfil})


#def documentos_inspector_estado(request, pk_estado):
#    usuario = request.user
#    perfil = 'css/' + usuario.persona.perfilCSS
#    estado = get_object_or_404(Estado, pk=pk_estado)
#    fecha = estado.timestamp
#    fecha_str = datetime.strftime(fecha, '%d/%m/%Y %H:%M')
#    documentos = estado.tramite.documentos.all()
#    documentos_fecha = filter(lambda e:(datetime.strftime(e.fecha, '%d/%m/%Y %H:%M') == fecha_str), documentos)
#    contexto= {'documentos_de_fecha': documentos_fecha, "perfil": perfil}
#    return render(request, 'persona/inspector/documentos_del_estado.html', contexto)


'''
jefeinspector ----------------------------------------------------------------------------------------------------
'''


@login_required(login_url="login")
@grupo_requerido('jefeinspector')
def mostrar_jefe_inspector(request):
    usuario = request.user
    perfil = 'css/' + usuario.persona.perfilCSS
    values = {
        "perfil": perfil,
        "ctxtramitesconinspeccion": tramite_con_inspecciones_list(),
        "ctxtramitesagendados": tramites_agendados_por_jefeinspector(request),
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
    argumentos = [FinalObraTotalSolicitado] # falta conCorreccionesInspeccion
    tramites = Tramite.objects.en_estado(argumentos)
    contexto = {'tramites': tramites}
    return contexto

def tramites_agendados_por_jefeinspector(request):
    usuario = request.user
    argumentos = [AgendadoInspeccionFinal]
    tramites = Tramite.objects.en_estado(argumentos)
    tramites_del_inspector = filter(lambda t: t.estado().usuario == usuario, tramites)
    return tramites_del_inspector


def agendar_inspeccion_final(request, pk_tramite):
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    fecha = convertidor_de_fechas(request.GET["msg"])
    tramite.hacer(Tramite.AGENDAR_INSPECCION, usuario=request.user, fecha_inspeccion=fecha, inspector=request.user)
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
    return redirect('jefeinspector')

def rechazar_inspeccion_final(request, pk_tramite):
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    tramite.hacer(Tramite.CORREGIR, request.user, request.POST["observaciones"])
    messages.add_message(request, messages.ERROR, 'Inspeccion final rechazada')
    return redirect('jefeinspector')


def aceptar_inspeccion_final(request, pk_tramite):
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    tramite.hacer(Tramite.APROBAR_INSPECCION, request.user)
    messages.add_message(request, messages.SUCCESS, 'Inspeccion final aprobada')
    return redirect('jefeinspector')


def ver_inspecciones(request, pk_tramite):
    pk = int(pk_tramite)
    estados = Estado.objects.all()
    estados_de_tramite = filter(lambda e: (e.tramite.pk == pk), estados)
    estados = filter(lambda e: (e.tipo == 9), estados_de_tramite)
    usuario = request.user
    perfil = 'css/' + usuario.persona.perfilCSS
    contexto = {'estados': estados, "perfil": perfil}
    return render(request, 'persona/jefe_inspector/vista_de_inspecciones.html',contexto)


'''
director ---------------------------------------------------------------------------------------------------------
'''

@login_required(login_url="login")
@grupo_requerido('director')
def mostrar_director(request):
    usuario = request.user
    perfil = 'css/' + usuario.persona.perfilCSS
    values = {
        "perfil": perfil,
        "datos_usuario": empleados(),
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


def empleados():
    usuarios = Usuario.objects.all()
    empleados = []
    for u in usuarios:
        lista = list(u.groups.values_list('name', flat=True))
        for i in range(len(lista)):
            if lista[i] != 'profesional' and lista[i] != 'propietario':
                if u not in empleados:
                    empleados.append(u)
    return empleados


def ver_listado_todos_tramites(request):
    usuario = request.user
    perfil = 'css/' + usuario.persona.perfilCSS
    argumentos = [Iniciado, Aceptado, Visado, Corregido, AgendadoInspeccion, ConInspeccion, Inspeccionado, FinalObraSolicitado]
    tramites = Tramite.objects.en_estado(argumentos)
    estados = []
    for t in tramites:
        estados.append(t.estado().tipo)
    estados_cant = dict(collections.Counter(estados))
    for n in range(1, 9):
        if (not estados_cant.has_key(n)):
            estados_cant.setdefault(n, 0)
    estados_datos = estados_cant.values()
    perfil = 'css/' + usuario.persona.perfilCSS
    contexto = {'todos_los_tramites': tramites, "datos_estados":estados_datos, "label_estados":argumentos, "perfil" : perfil}
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
    usuarios = empleados()
    usuario = request.user
    perfil = 'css/' + usuario.persona.perfilCSS
    return render(request, 'persona/director/vista_de_usuarios.html', {'todos_los_usuarios': usuarios, "label_grupos": label_grupos, "datos_grupos": datos_grupos,  "perfil": perfil})


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


def documentos_del_estado(request, pk_estado):
    usuario = request.user
    perfil = 'css/' + usuario.persona.perfilCSS
    estado = get_object_or_404(Estado, pk=pk_estado)
    fecha = estado.timestamp
    fecha_str = datetime.strftime(fecha, '%d/%m/%Y %H:%M')
    documentos = estado.tramite.documentos.all()
    documentos_fecha = filter(lambda e:(datetime.strftime(e.fecha, '%d/%m/%Y %H:%M') == fecha_str), documentos)
    contexto= {'documentos_de_fecha': documentos_fecha, "perfil": perfil}
    return render(request, 'persona/director/documentos_del_estado.html', contexto)


def ver_actividad_usuario(request, usuario):

    '''trabajando en esto'''

    usuarios = Usuario.objects.all()
    usuario_req = filter(lambda u: (str(u) == usuario), usuarios)
    estados = Estado.objects.all()
    estados_usuario_req = filter(lambda estado:(str(estado.usuario) == str(usuario_req[0])), estados)

    fechas_del_estado = []
    for e in estados_usuario_req:
        #print ("-----------------------")
        #print (e.tipo)
        #print (e.tramite)
        #print (e.usuario)
        #print (e.timestamp)
        if (e.timestamp.strftime("%d/%m/%Y")) not in fechas_del_estado:
            fechas_del_estado.append(e.timestamp.strftime("%d/%m/%Y"))

    user = request.user
    perfil = 'css/' + user.persona.perfilCSS
    return render(request, 'persona/director/vista_de_actividad_usuario.html', {"perfil": perfil})

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


'''
general-------------------------------------------------------------------------------------------------------
'''

def cambiar_perfil(request):
    usuario = request.user
    if request.method == "POST":
        estilo = request.POST["estiloCSS"]
        usuario.persona.modificarPerfilCSS(estilo)
        return redirect(usuario.get_view_name())


'''
No se de donde son estos -------------------------------------------------------------------------------------
'''

#def tramite_visados_list():
#    tramites = Tramite.objects.en_estado(Visado)
#    contexto = {'tramites': tramites}
#    return contexto


#def mostrar_popup_datos_agendar():
#    pass


def alta_persona(request):
    if request.method == "POST":
        form = FormularioPersona(request.POST)
        if form.is_valid():
            persona = form.save()
            persona.save()
    else:
        form = FormularioPersona()
    return render(request, 'persona/alta/alta_persona.html', {'form': form})
