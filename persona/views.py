from django.shortcuts import render, redirect


from .forms import *
from tipos.forms import *

def mostrar_inicio(request):
    return render(request, 'persona/inicio/base.html', {})

def mostrar_index(request):
    return render(request, 'persona/inicio/index.html')

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

def mostrar_visador(request):
    return render(request, 'persona/visador/visador.html')

def mostrar_visar(request):
    return render(request, 'persona/visador/visar.html')

def mostrar_director(request):
    alta_tipo_documento_form = FormularioTipoDocumento()
    alta_persona_form = FormularioPersona()
    alta_usuario_form = FormularioUsuario()

    if 'guardar_tipo_documento' in request.POST:

        if request.method == "POST":
            alta_tipo_documento_form = FormularioTipoDocumento(request.POST)
            if alta_tipo_documento_form.is_valid():
                tipo_documento = alta_tipo_documento_form.save()
                tipo_documento.save()
        else:
            alta_tipo_documento_form = FormularioTipoDocumento()

    if 'guardar_persona' in request.POST:

        if request.method == "POST":
            alta_persona_form = FormularioPersona(request.POST)
            if alta_persona_form.is_valid():
                persona = alta_persona_form.save()
                persona.save()
        else:
            alta_persona_form = FormularioPersona()


    return render(request, 'persona/director/director.html', {'alta_persona_form':alta_persona_form, 'alta_tipo_documento_form':alta_tipo_documento_form,
                    'alta_usuario_form':alta_usuario_form})


def alta_persona(request):

    if request.method == "POST":
        form = FormularioPersona(request.POST)
        if form.is_valid():
            persona = form.save()
            persona.save()
    else:
        form = FormularioPersona()
    return render(request, 'persona/alta/alta_persona.html', {'form': form})

def mostrar_administrativo(request):
    return render(request, 'persona/administrativo/Administrativo.html',{'FormularioProfesional':FormularioProfesional})
#return render(request, 'persona/director/director.html', {'alta_persona_form':alta_persona_form, 'alta_tipo_documento_form':alta_tipo_documento_form})


#Lo que se muestra en el template de administrativo

from django.http import HttpResponse
from django import forms
from persona.models import Persona, Profesional
from persona.forms import FormularioProfesional


def profesional_view(request):
    if request.method == 'POST':
        form = FormularioProfesional(request.POST)
        if form.is_valid():
            form.save()
        return redirect('persona/administrativo/profesional_form.html')
    else:
        form = FormularioProfesional()

    return render(request, 'persona/administrativo/profesional_form.html',{'form':form})

def profesional_list(request):
    persona = Persona.objects.all()
    contexto = {'personas': persona}
    #return render(request, 'persona/administrativo/profesional_list.html', contexto)
    return render(request, 'persona/administrativo/Administrativo.html', contexto)

