from django.shortcuts import render

from .forms import *

def mostrar_inicio(request):
    return render(request, 'inicio/base.html', {})

def mostrar_index(request):
    return render(request, 'inicio/index.html')

def mostrar_inspector(request):
    return render(request, 'inspector/inspector.html', {})

def mostrar_profesional(request):
    form = FormularioProfesional()
    return render(request, 'profesional/profesional.html',{'form':form})

def mostrar_jefe_inspector(request):
    return render(request, 'jefe_inspector/jefe_inspector.html')

def mostrar_propietario(request):
    form = FormularioPropietario()
    return render(request, 'propietario/propietario.html',{'form':form})

def mostrar_visador(request):
    return render(request, 'visador/visador.html')

def mostrar_visar(request):
    return render(request, 'visador/visar.html')

def alta_persona(request):
    #Aca tengo que instanciar el formulario y se lo paso por parametro a la plantilla y se muestra "Guala!"
    #form = FormularioPersona()
    #return render(request, 'persona/alta_persona.html', {'form': form})

    if request.method == "POST":
        form = FormularioPersona(request.POST)
        if form.is_valid():
            persona = form.save()
            persona.save()
    else:
        form = FormularioPersona()

    return render(request, 'persona/alta_persona.html', {'form': form})
