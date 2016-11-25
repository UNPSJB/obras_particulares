from django.conf.urls import include, url
from django.contrib.auth.decorators import login_required
from . import views
from tramite.models import *
from persona.views import ver_un_certificado
from persona.views import ver_documentos_tramite_profesional
from persona.views import ver_documentos_tramite_administrativo
from persona.views import aceptar_tramite




urlpatterns = [

    url(r'^profesional$', views.mostrar_profesional, name="profesional"),
    url(r'^inspector$', views.mostrar_inspector, name="inspector"),
    url(r'^jefeinspector$', views.mostrar_jefe_inspector, name="jefe_inspector"),
    url(r'^propietario$', views.mostrar_propietario, name="propietario"),
    url(r'^visador$', views.mostrar_visador, name="visador"),
    url(r'^altapersona$', views.alta_persona, name="alta_persona"),
    url(r'^director$', views.mostrar_director, name="director"),
    url(r'^administrativo$', views.mostrar_administrativo, name="administrativo"),
    url(r'^administrativo/tramite_listar$', views.listado_de_tramites_iniciados, name="tramite_listar"),

    url(r'^rechazar_tramite/(?P<pk_tramite>\d+)/$', views.rechazar_tramite, name="rechazar_tramite"),
    url(r'^aceptar_tramite/(?P<pk_tramite>\d+)/$', views.aceptar_tramite, name="aceptar_tramite"),


    url(r'^crearusuario/(?P<pk_persona>\d+)/$', views.crear_usuario, name="crear_usuario"),

    url(r'^profesional/estado_tramite$', views.listado_tramites_de_profesional, name="estado_tramite"),

    url(r'^solicitud_final_obra_parcial/(?P<pk_tramite>\d+)/$', views.solicitud_final_obra_parcial, name="solicitud_final_obra_parcial"),
    url(r'^solicitud_final_obra_total/(?P<pk_tramite>\d+)/$', views.solicitud_final_obra_total, name="solicitud_final_obra_total"),

    url(r'^habilitar_final_obra/(?P<pk_tramite>\d+)/$', views.habilitar_final_obra, name="habilitar_final_obra"),

    url(r'^ver_certificado/(?P<pk>\d+)/$', ver_un_certificado.as_view(), name="ver_certificado"),

    url(r'^ver_documentos_tramite_profesional/(?P<pk_tramite>\d+)/$', views.ver_documentos_tramite_profesional, name="ver_documentos_tramite_profesional"),

    url(r'^documentos_tramite_administrativo/(?P<pk_tramite>\d+)/$', views.ver_documentos_tramite_administrativo, name="ver_documentos_tramite_administrativo"),

    url(r'^aceptar_tramite/(?P<pk_tramite>\d+)/$', views.aceptar_tramite, name="aceptar_tramite"),
    #visado
    url(r'^ver_documentos_para_visado/(?P<pk_tramite>\d+)/$', views.ver_documentos_para_visado,name="ver_documentos_para_visado"),
    url(r'^aprobar_visado/(?P<pk_tramite>\d+)/$', views.aprobar_visado, name="aprobar_visado"),
    url(r'^no_aprobar_visado/(?P<pk_tramite>\d+)/$', views.no_aprobar_visado, name="no_aprobar_visado"),
]
