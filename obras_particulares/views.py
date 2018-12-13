from persona import *
from persona.forms import *
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from . import forms


def login_view(request):
    '''
    Funcion login view:
    Se encarga de loguear un nuevo usuario dentro del sistema
    :param request: Requerimiento HTTP.
    '''
    if request.method == 'POST':
        user = authenticate(username=request.POST['username'], password=request.POST['password'])
        if user is not None and user.is_active :
            login(request, user)
            return redirect(user.get_view_name())
        else:
            messages.add_message(request, messages.WARNING, 'Clave o usuario incorrecto.')
    return redirect("home")


def logout_view(request):
    '''
    Funcion logout view:
    Se encarga de cerrar la sesion activa de un usuario dentro del sistema
    :param request: Requerimiento HTTP.
    '''
    logout(request)
    return redirect("home")


def home(request):
    '''
    Funcion home:
    Se encarga de renderizar un nuevo formulario de ingreso de un profesional en el sistema
    :param request: Requerimiento HTTP.
    :return: Devuelve un formulario de profesional.
    '''
    try:
        usuario = request.user
        return redirect(usuario.get_view_name()) #cuando estoy loqueado y quiero ir a localhost/8000 me devuelve a la vista que me corresponde. no al inicio!
    except Exception as e:
        pass #cuando no estoy logueado vengo a parar aca y sigo el camino normal de abajo.

    if request.method == "POST":
        form = FormularioProfesional(request.POST, request.FILES)
        if form.is_valid():
            profesional = form.save()
            profesional.save()
            messages.add_message(request, messages.SUCCESS, "Solicitud de Registro Enviada")
            return redirect('home')
        else:
            messages.add_message(request, messages.ERROR, "Error de carga de formulario. Revise los datos ingresados.")
    else:
        form = FormularioProfesional()
    return render(request, 'home.html',{'login_usuario_form': forms.FormularioLogin(),'form':form})


def grupo_requerido(*grupos):
    '''
    Funcion grupo requerido:
    Se encarga de verificar que un usuario posea determinados permisos para acceder a las vistas
    :param grupos: conjunto de grupos disponibles en el sistema
    :return: vista a la que puede acceder un usuario.
    '''
    def view_funct(f):
        def func_wrapped(request, *args, **kwargs):
            usuario = request.user
            if bool(usuario.groups.filter(name__in=grupos)) | usuario.is_superuser:
                return f(request, *args, **kwargs)
            else:
                return redirect(usuario.get_view_name())
        return func_wrapped
    return view_funct
