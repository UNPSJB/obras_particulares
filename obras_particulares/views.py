from persona.forms import *
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from . import forms

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        print(username)
        password = request.POST['password']
        print(password)
        user = authenticate(username=request.POST['username'], password=request.POST['password'])
        print(user)
        if user is not None and user.is_active :
            login(request, user)
            return redirect(user.get_view_name())
        else:
            messages.add_message(request, messages.WARNING, 'Clave o usuario incorrecto.')
    return redirect("home")

def logout_view(request):
    logout(request)
    return redirect("home")

def home(request):
    form= FormularioProfesional()
    if request.method == "POST":
        form = FormularioProfesional(request.POST, request.FILES)
        if form.is_valid():
            profesional = form.save()
            profesional.save()
            #messages.add_message(request, messages.SUCCESS, "Soliciud de Registro Enviada")
    else:
        form = FormularioProfesional()
    return render(request, 'home.html',{'login_usuario_form': forms.FormularioLogin,'form':form})
