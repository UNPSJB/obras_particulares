
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import  login_required
from .forms import *
from tipos.forms import *
from obras_particulares.views import *

def alta_tramite(request):
	form = FormularioTramite()
	return render(request, 'alta/alta_tramite.html', {'form': form})
