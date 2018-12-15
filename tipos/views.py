from django.shortcuts import render, redirect
from .models import *
from .forms import *
from django.contrib import messages

def mostrar_tipoDocumento(request):
    form = FormularioTipoDocumento()
    return render(request, 'tipos/tipo_documento/tipoDocumento.html',{'form':form})

def alta_tipoObra(request):
    if request.method == "POST":
        form = FormularioTipoObra(request.POST)
        if form.is_valid():
            tipo_obra = form.save()
    else:
        form = FormularioTipoObra()
    return render(request, 'tipos/tipo_obra/tipoObra.html', {'form': form})


def alta_tipoDocumento(request):
    if request.method == "POST":
        form = FormularioTipoDocumento(request.POST)
        if form.is_valid():
            tipo_documento = form.save(commit=False)
            tipo_documento.save()
    else:
        form = FormularioTipoDocumento()

    return render(request, 'tipos/tipo_documento/tipoDocumento.html', {'form': form})

"""
Metodo que se encarga de activar un tipo de documento
"""
def activar(request, pk_tipo_documento):
        tipo_documento = TipoDocumento.objects.filter(id=pk_tipo_documento).first()
        tipo_documento.activo = True
        tipo_documento.save();
        mensaje = "Se activo correctamente el tipo de documento. " + tipo_documento.nombre
        messages.add_message(request, messages.SUCCESS, mensaje)
        return redirect("director")
        
"""
Metodo que se encarga de desactivar un tipo de documento
"""
def desactivar(request, pk_tipo_documento):
        tipo_documento = TipoDocumento.objects.filter(id=pk_tipo_documento).first()
        tipo_documento.activo = False
        tipo_documento.save();
        mensaje = "Se desactivo correctamente el tipo de documento. " + tipo_documento.nombre
        messages.add_message(request, messages.SUCCESS, mensaje)
        return redirect("director")
        
