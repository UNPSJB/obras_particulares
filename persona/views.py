from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import  login_required
from .forms import *
from tipos.forms import *
from obras_particulares.views import *
from tramite.forms import FormularioTramite
from tramite.models import Tramite


def mostrar_inspector(request):
    return render(request, 'persona/inspector/inspector.html', {})

def mostrar_profesional(request):
    formulario_busqueda_propietario = FormularioBusquedaPropietario()
    tipos_de_documentos_requeridos = TipoDocumento.get_tipos_documentos_para_momento("INICIAR")
    print(tipos_de_documentos_requeridos)
    """if request.method == "POST":
        formulario_busqueda_propietario = FormularioBusquedaPropietario(request.POST)
        if formulario_busqueda_propietario.is_valid():
            propietario_form = FormularioPropietario()
        else:
            formulario_busqueda_propietario = FormularioBusquedaPropietario()"""

    return render(request, 'persona/profesional/profesional.html',{'busqueda_propietario_form':formulario_busqueda_propietario,
                                                                   'tipos_de_documentos_requeridos': tipos_de_documentos_requeridos})

def mostrar_jefe_inspector(request):
    return render(request, 'persona/jefe_inspector/jefe_inspector.html')


def mostrar_propietario(request):
    form = FormularioPropietario()
    return render(request, 'persona/propietario/propietario.html',{'form':form})


@login_required(login_url="login")
@grupo_requerido('visador')
def mostrar_visador(request):
    return render(request, 'persona/visador/visador.html')

@login_required(login_url="login")
@grupo_requerido('visador')
def mostrar_visar(request):
    return render(request, 'persona/visador/visar.html')


FORMS_DIRECTOR = {(k.NAME, k.SUBMIT): k for k in [
    FormularioTipoDocumento,
    FormularioUsuarioPersona,  #este formulario no se necesitaria, solo se dan de alta visador, inspector y administrativo
    FormularioTipoObra,
    FormularioTipoDocumento,
    FormularioAdministrativo,
    FormularioInspector,
    FormularioVisador

]}

@login_required(login_url="login")
@grupo_requerido('director')
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

@login_required(login_url="login")
@grupo_requerido('administrativo')
def mostrar_administrativo(request):
    contexto = profesional_list(request)
    return render(request, 'persona/administrativo/administrativo.html', contexto)


def crear_usuario(request, pk_persona):
    usuario = request.user
    persona = get_object_or_404(Persona, pk=pk_persona)
    creado, password, usuario_creado = persona.crear_usuario()
    if creado:
        messages.add_message(request, messages.SUCCESS, 'usuario creado.')
        # Mandar correo al  nuevo usuario con su usurio y clave
        print("Mando correo de creado")
    else:
        print("Mando correo informando que se cambio algo en su cuenta de usuario")
    return redirect(usuario.get_view_name())


def profesional_list(request):
    personas = Persona.objects.all()
    profesionales = filter(lambda persona: (persona.usuario is None and persona.profesional is not None), personas)
    contexto = {'personas': profesionales}
    return contexto


def mostrar_tramite(request):
    tramite = Tramite.objects.all()
    contexto = { 'tramites': tramite}
    return render(request, 'persona/administrativo/tramite_list.html', contexto)
