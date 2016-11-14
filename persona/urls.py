from django.conf.urls import include, url
from django.contrib.auth.decorators import login_required
from . import views
from tramite.models import *

urlpatterns = [

    url(r'^profesional$', views.mostrar_profesional, name="profesional"),
    url(r'^inspector$', views.mostrar_inspector, name="inspector"),
    url(r'^jefeinspector$', views.mostrar_jefe_inspector, name="jefe_inspector"),
    url(r'^propietario$', views.mostrar_propietario, name="propietario"),
    url(r'^visador$', views.mostrar_visador, name="visador"),
    url(r'^visar$', views.mostrar_visar, name="visar"),
    url(r'^altapersona$', views.alta_persona, name="alta_persona"),
    url(r'^director$', views.mostrar_director, name="director"),
    url(r'^administrativo$', views.mostrar_administrativo, name="administrativo"),
    url(r'^administrativo/tramite_listar$', views.tramite_list, name="tramite_listar"),

    url(r'^rechazar_tramite/(?P<pk_tramite>\d+)/$', views.rechazar_tramite, name="rechazar_tramite"),
    url(r'^aceptar_tramite/(?P<pk_tramite>\d+)/$', views.aceptar_tramite, name="aceptar_tramite"),


    url(r'^crearusuario/(?P<pk_persona>\d+)/$', views.crear_usuario, name="crear_usuario"),

    url(r'^profesional/estado_tramite$', views.consultar_estado_tramite_list, name="estado_tramite")

]
