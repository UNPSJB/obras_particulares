from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import *
from tipos.forms import *

def mostrar_index(request):

    solicitud_registro_profesional_form = FormularioProfesional()
    return render(request, 'persona/inicio/index.html',
        {'profesional_form':solicitud_registro_profesional_form})


    login_usuario_form = FormularioUsuario()
    if request.method == "POST":
        form = FormularioProfesional(request.POST, request.FILES)
        if form.is_valid():
            profesional = form.save()
            profesional.save()
    else:
        form = FormularioProfesional()

    return render(request, 'persona/inicio/index.html', {'form':form, 'login_usuario_form': login_usuario_form})


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

FORMS_DIRECTOR = {
    ('tipo_documento_form', 'tipo_documento_submit'): FormularioTipoDocumento,
    ('usuario_persona_form', 'usuario_persona_submit'): FormularioUsuarioPersona,
    ('tipo_obra_form', 'tipo_obra_submit'): FormularioTipoObra,
    ('tipo_documento_form', 'tipo_documento_submit'): FormularioTipoDocumento,
}

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
