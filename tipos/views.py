from django.shortcuts import render

from .forms import *

def mostrar_tipoDocumento(request):
    form = FormularioTipoDocumento()
    return render(request, 'tipo_documento/tipoDocumento.html',{'form':form})


def alta_tipoDocumento(request):
    if request.method == "POST":
        form = FormularioTipoDocumento(request.POST)
        if form.is_valid():
            tipoDocumento = form.save(commit=False)
            tipoDocumento.save()
    else:
        form = FormularioTipoDocumento()

    return render(request, 'tipo_documento/tipoDocumento.html', {'form': form})
