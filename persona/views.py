from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import  login_required
from .forms import *
from django.contrib import messages
from tipos.forms import *
from obras_particulares.views import *
from tramite.forms import Formulario_Iniciar_Tramite
from tramite.models import *


def mostrar_inspector(request):
    return render(request, 'persona/inspector/inspector.html', {})

def mostrar_profesional(request):
    tipos_de_documentos_requeridos = TipoDocumento.get_tipos_documentos_para_momento("INICIAR")
    tramite_form = Formulario_Iniciar_Tramite()
    formulario_busqueda_propietario = FormularioBusquedaPropietario()
    propietario_form = FormularioPropietario()
    propietario = True
    if request.method == "POST":

        if 'busqueda_propietario_submit' in request.POST:

            formulario_busqueda_propietario = FormularioBusquedaPropietario(request.POST)
            if formulario_busqueda_propietario.is_valid(): #si no lanza la excepcion entra aca (si no existe)
                messages.add_message(request, messages.WARNING, 'El propietario no existe debe darlo de alta')
                propietario_form = FormularioPropietario()
                propietario = False

            else:   #propietario existe
                dni_propietario = request.POST['dni']
                propietario = Propietario.objects.get(dni=dni_propietario)
                propietario_form = FormularioPropietario(instance=propietario)

        if 'tramite_submit' in request.POST:

            tramite_form = Formulario_Iniciar_Tramite(request.POST)
            if tramite_form.is_valid():
                tramite_form.save()

    else:
        formulario_busqueda_propietario = FormularioBusquedaPropietario()
        propietario_form = FormularioPropietario()

    return render(request, 'persona/profesional/profesional.html',{'busqueda_propietario_form':formulario_busqueda_propietario,
                                                                   'tipos_de_documentos_requeridos': tipos_de_documentos_requeridos,
                                                                   'tramite_form': tramite_form,
                                                                   'propietario_form': propietario_form, "propietario": propietario})

"""def mostrar_profesional(request):
    tipos_de_documentos_requeridos = TipoDocumento.get_tipos_documentos_para_momento("INICIAR")
    tramite_form = FormularioTramite()

    if request.method == "POST":
        formulario_busqueda_propietario = FormularioBusquedaPropietario(request.POST)
    else:
        formulario_busqueda_propietario = FormularioBusquedaPropietario()

    return render(request, 'persona/profesional/profesional.html',
                  {'busqueda_propietario_form': formulario_busqueda_propietario,
                   'tipos_de_documentos_requeridos': tipos_de_documentos_requeridos,
                   'tramite_form': tramite_form,})"""



def mostrar_jefe_inspector(request):
    return render(request, 'persona/jefe_inspector/jefe_inspector.html')


def mostrar_propietario(request):
    form = FormularioPropietario()
    return render(request, 'persona/propietario/propietario.html',{'form':form})


@login_required(login_url="login")
@grupo_requerido('visador')
def mostrar_visador(request):
    return render(request, 'persona/visador/visador.html')

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

@login_required(login_url="login")
@grupo_requerido('administrativo')
def mostrar_administrativo(request):
    contexto = profesional_list(request)
    return render(request, 'persona/administrativo/administrativo.html', contexto)


from django.core.mail import send_mail

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
            'Usted ya puede acceder al sistema',
            'infosopunpsjb@gmail.com',
            [persona.mail],
            fail_silently=False,
        )

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
    contexto = {'propietarios': propietario}
    return render(request, 'persona/administrativo/propietario_list.html', contexto)


def tramite_list(request):
    tramite = Tramite.objects.all()
    contexto = {'tramites': tramite}
    return render(request, 'persona/administrativo/tramite_list.html', contexto)

def tramite_corregidos_list(request):
    tramite = Tramite.objects.all()
    contexto = {'tramites': tramite}
    return render(request, 'persona/administrativo/tramite_corregidos_list.html', contexto)

def solicitud_final_obra_list(request):
    tramite = Tramite.objects.all()
    contexto = {'tramites': tramite}
    return render(request, 'persona/administrativo/solicitud_final_obra_list.html', contexto)
