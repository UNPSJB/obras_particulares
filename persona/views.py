from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import  login_required
from .forms import *
from tipos.forms import *
from obras_particulares.views import *


def mostrar_inspector(request):
    return render(request, 'persona/inspector/inspector.html', {})

def mostrar_profesional(request):
    form = FormularioProfesional()
    return render(request, 'persona/profesional/profesional.html',{'form':form})

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
    return render(request, 'persona/administrativo/administrativo.html',contexto)
#    return render(request, 'persona/administrativo/administrativo.html',{'FormularioProfesional':FormularioProfesional}, contexto)

#


def habilitar(request):
    print ("HOLA")
    id_persona = request.get(persona.id)
    print (id_persona)
    if request.POST:

        persona.usuario = Usuario.objects.create_user(username=persona.mail,
                                                      email=persona.mail,
                                                      password="usuario217")


    return redirect("administrativo")


def profesional_list(request):
    persona = Persona.objects.all()
    contexto = {'personas': persona}
    return contexto


from tramite.forms import FormularioTramite
from tramite.models import Tramite

def mostrar_tramite(request):
    tramite = Tramite.objects.all()
    contexto = { 'tramites': tramite}
    return render(request, 'persona/administrativo/tramite_list.html', contexto)

