from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import *
from tipos.forms import *

def mostrar_index(request):
<<<<<<< HEAD
    solicitud_registro_profesional_form = FormularioProfesional()
    return render(request, 'persona/inicio/index.html',
        {'profesional_form':solicitud_registro_profesional_form})
=======

    login_usuario_form = FormularioUsuario()
    if request.method == "POST":
        form = FormularioProfesional(request.POST, request.FILES)
        if form.is_valid():
            profesional = form.save()
            profesional.save()
    else:
        form = FormularioProfesional()

    return render(request, 'persona/inicio/index.html', {'form':form, 'login_usuario_form': login_usuario_form})
>>>>>>> refs/remotes/origin/master

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
    alta_usuario_persona_form = FormularioUsuarioPersona()
    alta_tipo_de_obra_form = FormularioTipoObra()

    if 'guardar_tipo_documento' in request.POST:

        if request.method == "POST":
            alta_tipo_documento_form = FormularioTipoDocumento(request.POST)
            if alta_tipo_documento_form.is_valid():
                tipo_documento = alta_tipo_documento_form.save()
                tipo_documento.save()
        else:
            alta_tipo_documento_form = FormularioTipoDocumento()

    elif 'guardar_tipo_de_obra' in request.POST:

        if request.method == "POST":
            alta_tipo_de_obra_form = FormularioTipoObra(request.POST)
            if alta_tipo_de_obra_form.is_valid():
                tipo_de_obra = alta_tipo_de_obra_form.save()
                tipo_de_obra.save()
        else:
            alta_tipo_de_obra_form = FormularioTipoObra()

    if 'guardar_persona' in  request.POST:

        if request.method == "POST":
            alta_usuario_persona_form = FormularioUsuarioPersona(request.POST)
            if alta_usuario_persona_form.is_valid():
                usuario_persona = alta_usuario_persona_form.save()
                usuario_persona.save()
        else:
            alta_usuario_persona_form = FormularioUsuarioPersona()


    return render(request, 'persona/director/director.html', {
        'alta_tipo_documento_form':alta_tipo_documento_form,
        'alta_usuario_persona_form':alta_usuario_persona_form,
        'alta_tipo_de_obra_form':alta_tipo_de_obra_form})


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


def profesional_list(request):
    persona = Persona.objects.all()
    contexto = {'personas': persona}
    return render(request, 'persona/administrativo/administrativo.html', contexto)



#Nuevo profesional en el registro del municio
'''def alta_profesional(request):
    if request.method == "POST":
        form = FormularioProfesional(request.POST)
        if form.is_valid():

            profesional = form.save()
            profesional.save()
    else:
        form = FormularioProfesional()
    return render(request, 'persona/alta/alta_profesional.html', {'form': form})
'''
def nuevo(request):
    form = FormularioProfesional()
    if request.method == "POST":
        form = FormularioProfesional(request.POST)
        if form.is_valid():
            profesional = form.save()
            profesional.save()
    else:
        form = FormularioProfesional()
    return render(request, 'persona/inicio/login_nuevo_profesional.html', {'form':form})
