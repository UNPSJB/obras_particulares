
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import  login_required
from .forms import *
from obras_particulares.views import *
from . import app_settings
from django.views.static import serve
from django.http import HttpResponse, Http404


#agrgegar decorator
def alta_documento(request):
    '''
    Funcion alta documento:
    Se encarga de la creacion de un nuevo documento.
    :param request: Requerimiento HTTP.
    :return: Devuelve un formulario de documento.
    '''
    if request.method == "POST":
        form = FormularioDocumento(request.POST)
        if form.is_valid():
            documento = form.save(commit=False)
            documento.save()
    else:
        form = FormularioDocumento()
    return render(request, 'documento/alta/alta_documento.html', {'form': form})

def obtener_path(nivel_usuario):
    if nivel_usuario not in [1,2,3,4,5,6,7]:
        return app_settings.DOCUMENTATION_HTML_ROOT_INDICE
    if nivel_usuario == 1:
        return app_settings.DOCUMENTATION_HTML_ROOT_PROPIETARIO
    elif nivel_usuario == 2:
        return app_settings.DOCUMENTATION_HTML_ROOT_PROFESIONAL
    elif nivel_usuario == 3:
        return app_settings.DOCUMENTATION_HTML_ROOT_ADMINISTRATIVO
    elif nivel_usuario == 4:
        return app_settings.DOCUMENTATION_HTML_ROOT_VISADOR
    elif nivel_usuario == 5:
        return app_settings.DOCUMENTATION_HTML_ROOT_INSPECTOR
    elif nivel_usuario == 6:
        return app_settings.DOCUMENTATION_HTML_ROOT_DIRECTOR
    elif nivel_usuario == 7:
        return app_settings.DOCUMENTATION_HTML_ROOT_JEFEINSPECTOR

@login_required
def documentation(request, path='index.html'):
    nivel_usuario = app_settings.DOCUMENTATION_ACCESS_FUNCTION(request.user)
    ruta_documentacion = obtener_path(nivel_usuario)

    if True:  # not app_settings.DOCUMENTATION_XSENDFILE:
        return serve(
            request,
            path,
            ruta_documentacion)
    mimetype, encoding = mimetypes.guess_type(path)
    response = HttpResponse(mimetype=mimetype)

    response['Content-Encoding'] = encoding
    response['Content-Disposition'] = ''
    response['X-Accel-Redirect'] = "".join([ruta_documentacion, path])
    return response


def documentacion_indice(request, path='index.html'):
    nivel_usuario = app_settings.DOCUMENTATION_ACCESS_FUNCTION(request.user)
    ruta_documentacion = obtener_path(nivel_usuario)
    if True:  # not app_settings.DOCUMENTATION_XSENDFILE:
        return serve(
            request,
            path,
            ruta_documentacion)
    mimetype, encoding = mimetypes.guess_type(path)
    response = HttpResponse(mimetype=mimetype)

    response['Content-Encoding'] = encoding
    response['Content-Disposition'] = ''
    response['X-Accel-Redirect'] = "".join([ruta_documentacion, path])
    return response
