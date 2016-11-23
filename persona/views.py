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
from tramite.models import Tramite
from django.views.generic.detail import DetailView
#from documento.forms import *


@login_required(login_url="login")
@grupo_requerido('inspector')
def mostrar_inspector(request):
    contexto = {
        "ctxtramitesaceptados": tramite_aceptados_list(request),
    }
    return render(request, 'persona/inspector/inspector.html',contexto)

def tramite_aceptados_list(request):
    tramites = Tramite.objects.all()
    #tramites = filter(lambda tramite: (isinstance(tramite.estado_actual,Iniciado), tramites))
    contexto = {'tramites': tramites}
    return contexto

def mostrar_profesional(request):
    usuario = request.user
    tipos_de_documentos_requeridos = TipoDocumento.get_tipos_documentos_para_momento(TipoDocumento.INICIAR)
    FormularioDocumentoSet = FormularioDocumentoSetFactory(tipos_de_documentos_requeridos)
    inicial = metodo(tipos_de_documentos_requeridos)
    documento_set = FormularioDocumentoSet(initial=inicial)
    tramite_form = FormularioIniciarTramite(initial={'profesional':usuario.persona.profesional.pk})
    propietario_form = FormularioPropietario()
    propietario = None

    #contexto = listado_tramites_de_profesional(request)

    print("Estoy en mostrar profesional")

    if request.method == "POST":
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
            Tramite.new(usuario, propietario, usuario.persona.profesional,request.POST['tipo_obra'],request.POST['medidas'],request.POST['domicilio'],lista)
            tramite_form = FormularioIniciarTramite(initial={'profesional':usuario.persona.profesional.pk})
            propietario_form = None
    else:
        propietario_form = None

    contexto = {
        "ctxtramitesprofesional": listado_tramites_de_profesional(request),
        'tramite_form': tramite_form,
        'propietario_form': propietario_form,
        'documento_set': documento_set
    }


    return render(request, 'persona/profesional/profesional.html', contexto)

def mostrar_jefe_inspector(request):
    return render(request, 'persona/jefe_inspector/jefe_inspector.html')


def mostrar_propietario(request):
    form = FormularioPropietario()
    return render(request, 'persona/propietario/propietario.html',{'form':form})


@login_required(login_url="login")
@grupo_requerido('visador')
def mostrar_visador(request):
    contexto = tramites_aceptados(request)
    return render(request, 'persona/visador/visador.html', contexto)

@login_required(login_url="login")
@grupo_requerido('visador')
def mostrar_visar(request):
    return render(request, 'persona/visador/visar.html')


FORMS_DIRECTOR = {(k.NAME, k.SUBMIT): k for k in [
    FormularioTipoDocumento,
    FormularioUsuarioPersona,  #este formulario no se necesitaria, solo se dan de alta visador, inspector y administrativo
    FormularioTipoObra,
    FormularioTipoDocumento,
    FormularioAdministrativo,
    FormularioInspector,
    FormularioVisador

]}

@login_required(login_url="login")
@grupo_requerido('director')
def mostrar_director(request):
    usuario = request.user
    values = {}
    for form_name, submit_name in FORMS_DIRECTOR:
        KlassForm = FORMS_DIRECTOR[(form_name, submit_name)]
        if request.method == "POST" and submit_name in request.POST:
            _form = KlassForm(request.POST)
            if _form.is_valid():
                _form.save()
                return redirect(usuario.get_view_name())
            else:
                values["submit_name"] = submit_name
            values[form_name] = _form
        else:
            values[form_name] = KlassForm()

    return render(request, 'persona/director/director.html', values)


def alta_persona(request):
    if request.method == "POST":
        form = FormularioPersona(request.POST)
        if form.is_valid():
            persona = form.save()
            persona.save()
    else:
        form = FormularioPersona()
    return render(request, 'persona/alta/alta_persona.html', {'form': form})

def registrar_pago_tramite(request):

    print(request.FILES)
    if request.method == "POST":
        print("POST")
        archivo_pago_form = FormularioArchivoPago(request.POST, request.FILES)
        if archivo_pago_form.is_valid():
            Pago.procesar_pagos(request.FILES['pagos'])
    else:
        archivo_pago_form = FormularioArchivoPago()

    #formulario = {'archivo_pago_form' : archivo_pago_form}

    return archivo_pago_form


@login_required(login_url="login")
@grupo_requerido('administrativo')
def mostrar_administrativo(request):

    contexto = {
        "ctxprofesional": profesional_list(request),
        "ctxpropietario": propietario_list(request),
        "ctxtramite": tramite_list(request),
        "ctxtramitescorregidos": tramite_corregidos_list(request),
        "ctxsolicitudesfinalobra": solicitud_final_obra_list(request),
	    "ctxpago" : registrar_pago_tramite(request)

    }
    return render(request, 'persona/administrativo/administrativo.html', contexto)


def crear_usuario(request, pk_persona):
    usuario = request.user
    persona = get_object_or_404(Persona, pk=pk_persona)
    creado, password, usuario_creado = persona.crear_usuario()
    if creado:
        messages.add_message(request, messages.SUCCESS, 'usuario creado.')
        # Mandar correo al  nuevo usuario con su usurio y clave
        print("Mando correo de creado")
        send_mail(
            'Usuario habilitado',
            'Usted ya puede acceder al sistema: Nombre de usuario: '+persona.mail+' password: '+password,
            'infosopunpsjb@gmail.com',
            [persona.mail],
            fail_silently=False,
        )
        print (password)
    else:
        print("Mando correo informando que se cambio algo en su cuenta de usuario")

    return redirect(usuario.get_view_name())


def profesional_list(request):
    personas = Persona.objects.all()
    profesionales = filter(lambda persona: (persona.usuario is None and persona.profesional is not None), personas)
    contexto = {'personas': profesionales}
    return contexto

def propietario_list(request):
    propietarios = Propietario.objects.all()
    contexto = {'propietarios': propietarios}
    #return render(request, 'persona/administrativo/propietario_list.html', contexto)
    return contexto

# es el de tramites iniciados
def tramite_list(request):
    tramites = Tramite.objects.all()
    contexto = {'tramites': tramites}
    #return render(request, 'persona/administrativo/tramite_list.html', contexto)
    return contexto

def tramite_corregidos_list(request):
    tramites = Tramite.objects.all()
    #tramites = filter(lambda tramite: (tramite.estado_actual is  is not None), personas)
    contexto = {'tramites': tramites}

    return contexto


def listado_tramites_de_profesional(request):
    tramites = Tramite.objects.all()
    personas = Persona.objects.all()
    usuario = request.user

    lista_de_persona_que_esta_logueada = filter(lambda persona: (persona.usuario is not None and persona.usuario == usuario), personas)

    persona = lista_de_persona_que_esta_logueada.pop()  #Saco de la lista la persona porque no puedo seguir trabajando con una lista

    profesional = persona.get_profesional() #Me quedo con el atributo profesional de la persona

    tramites_de_profesional = filter(lambda tramite: (tramite.profesional == profesional), tramites)

    #contexto = {'tramites_de_profesional': tramites_de_profesional}
    return tramites_de_profesional



def aceptar_tramite(request, pk_tramite):
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    #poner la funcion que cambia de estado al tramite
    return redirect('administrativo')

def rechazar_tramite(request, pk_tramite):
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    #poner la funcion que cambia de estado al tramite
    return redirect('administrativo')


class ver_un_certificado(DetailView):
    model = Persona
    template_name = 'persona/administrativo/ver_certificado_profesional.html'

    def dispatch(self, *args, **kwargs):
        return super(ver_un_certificado, self).dispatch(*args, **kwargs)




@login_required(login_url="login")
@grupo_requerido('visador')
def mostrar_visar(request):
    contexto = tramites_aceptados(request)
    return render(request, 'persona/visador/visar.html', contexto)


def tramites_aceptados(request):
    aceptados = Tramite.objects.all()
    para_asignar = aceptados
    contexto = {'tramites_para_asignar': para_asignar}
    return contexto

def tramites_asignados(request):
    asignados = Tramite.objects.all()
    para_visar = asignados
    contexto = {'tramites_para_visar': para_visar}
    return contexto


def solicitud_final_obra_parcial(request, pk_tramite):
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    #poner la funcion que cambia de estado al tramite
    messages.add_message(request, messages.SUCCESS, 'final de obra parcial solicitado.')
    return redirect('profesional')

def solicitud_final_obra_total(request, pk_tramite):
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    #poner la funcion que cambia de estado al tramite

    messages.add_message(request, messages.SUCCESS, 'final de obra total solicitado.')
    return redirect('profesional')

def solicitud_final_obra_list(request):

    tramites = Tramite.objects.en_estado(Iniciado)

    print tramites

    contexto = {'tramites': tramites}
    #return render(request, 'persona/administrativo/solicitud_final_obra_list.html', contexto)
    return contexto

def habilitar_final_obra(request, pk_tramite):
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    #poner la funcion que cambia de estado al tramite
    tramite.hacer(tramite.ACEPTAR, request.user)
    messages.add_message(request, messages.SUCCESS, 'final de obra habilitado.')
    contexto = solicitud_final_obra_list(request)
    return render(request, 'persona/administrativo/administrativo.html', contexto)
