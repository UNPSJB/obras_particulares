from django.shortcuts import render

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
    return render(request, 'persona/director/director.html', {'alta_persona_form':alta_persona_form, 'alta_tipo_documento_form':alta_tipo_documento_form})


def alta_persona(request):
    #Aca tengo que instanciar el formulario y se lo paso por parametro a la plantilla y se muestra "Guala!"
    #form = FormularioPersona()
    #return render(request, 'alta/alta.html', {'form': form})

    if request.method == "POST":
        form = FormularioPersona(request.POST)
        if form.is_valid():
            persona = form.save()
            persona.save()
    else:
        form = FormularioPersona()

    return render(request, 'persona/alta/alta_persona.html', {'form': form})
