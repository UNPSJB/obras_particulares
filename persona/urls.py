from django.conf.urls import include, url
from django.contrib.auth.decorators import login_required
from . import views
from tramite.models import *
from persona.views import *





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
    url(r'^agendar_tramite/(?P<pk_tramite>\d+)/$', views.agendar_tramite, name="agendar_tramite"),



    url(r'^crearusuario/(?P<pk_persona>\d+)/$', views.crear_usuario, name="crear_usuario"),

    url(r'^profesional/estado_tramite$', views.listado_tramites_de_profesional, name="estado_tramite"),

    url(r'^solicitud_final_obra_propietario/(?P<pk_tramite>\d+)/$', views.propietario_solicita_final_obra, name="propietario_solicita_final_obra"),
    url(r'^solicitud_final_obra/(?P<pk_tramite>\d+)/$', views.profesional_solicita_final_obra, name="profesional_solicita_final_obra"),

    url(r'^habilitar_final_obra/(?P<pk_tramite>\d+)/$', views.habilitar_final_obra, name="habilitar_final_obra"),

    url(r'^ver_certificado/(?P<pk>\d+)/$', ver_un_certificado.as_view(), name="ver_certificado"),

    url(r'^ver_documentos_tramite_profesional/(?P<pk_tramite>\d+)/$', views.ver_documentos_tramite_profesional, name="ver_documentos_tramite_profesional"),
    url(r'^ver_documentos_corregidos/(?P<pk_tramite>\d+)/$', views.ver_documentos_corregidos,name="ver_documentos_corregidos"),
    url(r'^documentos_tramite_administrativo/(?P<pk_tramite>\d+)/$', views.ver_documentos_tramite_administrativo, name="ver_documentos_tramite_administrativo"),

    url(r'^aceptar_tramite/(?P<pk_tramite>\d+)/$', views.aceptar_tramite, name="aceptar_tramite"),
    #visado
    url(r'^ver_documentos_para_visado/(?P<pk_tramite>\d+)/$', views.ver_documentos_para_visado,name="ver_documentos_para_visado"),
    url(r'^aprobar_visado/(?P<pk_tramite>\d+)/$', views.aprobar_visado, name="aprobar_visado"),
    url(r'^no_aprobar_visado/(?P<pk_tramite>\d+)/$', views.no_aprobar_visado, name="no_aprobar_visado"),
    url(r'^ver_documentos_visados/(?P<pk_tramite>\d+)/$', views.ver_documentos_visados,name="ver_documentos_visados"),
    url(r'^vista_de_inspecciones/(?P<pk_tramite>\d+)/$', views.ver_inspecciones, name="ver_inspecciones"),
    url(r'^crearusuario/(?P<pk_propietario>\d+)/$', views.crear_usuario, name="crear_usuario"),
url(r'^enviar_correcciones/(?P<pk_tramite>\d+)/$', views.enviar_correcciones, name="enviar_correcciones"),

]
