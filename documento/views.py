
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import  login_required
from .forms import *
from obras_particulares.views import *


#agrgegar decorator
def alta_documento(request):
    if request.method == "POST":
        form = FormularioDocumento(request.POST)
        if form.is_valid():
            documento = form.save(commit=False)
            documento.save()
    else:
        form = FormularioDocumento()

    return render(request, 'documento/alta/alta_documento.html', {'form': form})
