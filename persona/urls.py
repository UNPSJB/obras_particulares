from django.conf.urls import include, url
from django.contrib.auth.decorators import login_required
from . import views
from tramite.models import *
from persona.views import *

urlpatterns = [

    #No me acuerdo de donde son - Acomodar esto!!!! -------------------------------------------------------------------

    url(r'^altapersona$', views.alta_persona, name="alta_persona"),
    url(r'^crearusuario/(?P<pk_persona>\d+)/$', views.crear_usuario, name="crear_usuario"),
    url(r'^aceptar_tramite/(?P<pk_tramite>\d+)/$', views.aceptar_tramite, name="aceptar_tramite"),

    # propietario ---------------------------------------------------------------------------------------------------
    url(r'^propietario$', views.mostrar_propietario, name="propietario"),
    url(r'^ver_historial_tramite/(?P<pk_tramite>\d+)/$', views.ver_historial_tramite, name="ver_historial_tramite"),
    url(r'^solicitud_final_obra_propietario/(?P<pk_tramite>\d+)/$', views.propietario_solicita_final_obra, name="propietario_solicita_final_obra"),
    url(r'^documentos_de_estado/(?P<pk_estado>\d+)/$', views.documentos_de_estado, name="documentos_de_estado"),
    url(r'^cargar_aprobacion_propietario/(?P<pk_tramite>\d+)/$', views.cargar_aprobacion_propietario, name="cargar_aprobacion_propietario"),
    url(r'^cargar_final_de_obra_total_propietario/(?P<pk_tramite>\d+)/$', views.cargar_final_de_obra_total_propietario, name="cargar_final_de_obra_total_propietario"),
    url(r'^cambiar_profesional_de_tramite/(?P<pk_tramite>\d+)/$', views.cambiar_profesional_de_tramite, name="cambiar_profesional_de_tramite"),

    # profesional ---------------------------------------------------------------------------------------------------
    url(r'^profesional$', views.mostrar_profesional, name="profesional"),
    url(r'^ver_documentos_tramite_profesional/(?P<pk_tramite>\d+)/$', views.ver_documentos_tramite_profesional, name="ver_documentos_tramite_profesional"),
    url(r'^ver_documentos_corregidos/(?P<pk_tramite>\d+)/$', views.ver_documentos_corregidos, name="ver_documentos_corregidos"),
    url(r'^solicitud_final_obra/(?P<pk_tramite>\d+)/$', views.profesional_solicita_final_obra, name="profesional_solicita_final_obra"),
    url(r'^solicitud_no_final_obra/(?P<pk_tramite>\d+)/$', views.profesional_solicita_no_final_obra, name="profesional_solicita_no_final_obra"),
    url(r'^solicitud_final_obra_parcial/(?P<pk_tramite>\d+)/$', views.profesional_solicita_final_obra_parcial,name="profesional_solicita_final_obra_parcial"),
    url(r'^profesional_solicita_aprobar_tramite/(?P<pk_tramite>\d+)/$', views.profesional_solicita_aprobar_tramite, name="profesional_solicita_aprobar_tramite"),
    url(r'^profesional_solicita_no_aprobar_tramite/(?P<pk_tramite>\d+)/$', views.profesional_solicita_no_aprobar_tramite,name="profesional_solicita_no_aprobar_tramite"),
    url(r'^enviar_correcciones/(?P<pk_tramite>\d+)/$', views.enviar_correcciones, name="enviar_correcciones"),
    url(r'^profesional/estado_tramite$', views.listado_tramites_de_profesional, name="estado_tramite"),
    url(r'^documento_de_estado/(?P<pk_estado>\d+)/$', views.documento_de_estado, name="documento_de_estado"),
    url(r'^cargar_final_de_obra_total_profesional/(?P<pk_tramite>\d+)/$', views.cargar_final_de_obra_total_profesional, name="cargar_final_de_obra_total_profesional"),
    url(r'^cargar_no_final_de_obra_total_profesional/(?P<pk_tramite>\d+)/$', views.cargar_no_final_de_obra_total_profesional, name="cargar_no_final_de_obra_total_profesional"),
    url(r'^cargar_no_aprobar_profesional/(?P<pk_tramite>\d+)/$', views.cargar_no_aprobar_profesional, name="cargar_no_aprobar_profesional"),

    # administrativo ------------------------------------------------------------------------------------------------
    url(r'^administrativo$', views.mostrar_administrativo, name="administrativo"),
    url(r'^crearusuario/(?P<pk_propietario>\d+)/$', views.crear_usuario, name="crear_usuario"),
    url(r'^administrativo/tramite_listar$', views.listado_de_tramites_iniciados, name="tramite_listar"),
    url(r'^ver_un_certificado/(?P<pk_persona>\d+)/$', views.ver_un_certificado, name="ver_un_certificado"),
    url(r'^documentos_tramite_administrativo/(?P<pk_tramite>\d+)/$', views.ver_documentos_tramite_administrativo, name="ver_documentos_tramite_administrativo"),
    url(r'^rechazar_tramite/(?P<pk_tramite>\d+)/$', views.rechazar_tramite, name="rechazar_tramite"),
    url(r'^aceptar_tramite/(?P<pk_tramite>\d+)/$', views.aceptar_tramite, name="aceptar_tramite"),
    url(r'^aprobar_tramite/(?P<pk_tramite>\d+)/$', views.aprobar_tramite, name="aprobar_tramite"),
    url(r'^no_aprobar_tramite/(?P<pk_tramite>\d+)/$', views.no_aprobar_tramite, name="no_aprobar_tramite"),
    url(r'^cargar_aprobacion/(?P<pk_tramite>\d+)/$', views.cargar_aprobacion, name="cargar_aprobacion"),
    url(r'^cargar_no_aprobacion/(?P<pk_tramite>\d+)/$', views.cargar_no_aprobacion, name="cargar_no_aprobacion"),
    url(r'^aprobar_final_de_obra/(?P<pk_tramite>\d+)/$', views.habilitar_final_obra, name="habilitar_final_obra"),
    url(r'^cargar_final_de_obra_total/(?P<pk_tramite>\d+)/$', views.cargar_final_de_obra_total,name="cargar_final_de_obra_total"),
    url(r'^dar_baja_tramite/(?P<pk_tramite>\d+)/$', views.dar_baja_tramite, name="dar_baja_tramite"),

    # visador -------------------------------------------------------------------------------------------------------
    url(r'^visador$', views.mostrar_visador, name="visador"),
    url(r'^agendar_tramite_para_visado/(?P<pk_tramite>\d+)/$', views.agendar_tramite_para_visado, name="agendar_tramite_para_visado"),
    url(r'^ver_documentos_para_visado/(?P<pk_tramite>\d+)/$', views.ver_documentos_para_visado, name="ver_documentos_para_visado"),
    url(r'^aprobar_visado/(?P<pk_tramite>\d+)/$', views.aprobar_visado, name="aprobar_visado"),
    url(r'^no_aprobar_visado/(?P<pk_tramite>\d+)/$', views.no_aprobar_visado, name="no_aprobar_visado"),
    url(r'^ver_documentos_visados/(?P<pk_estado>\d+)/$', views.ver_documentos_visados, name="ver_documentos_visados"),
    url(r'^reporte_tramites_aceptados_excel/', ReporteTramitesAceptadosExcel.as_view(), name="reporte_tramites_aceptados_excel"),
    url(r'^reporte_tramites_aceptados_pdf/$', login_required(ReporteTramitesAceptadosPdf.as_view()), name="reporte_tramites_aceptados_pdf"),

    # inspector -----------------------------------------------------------------------------------------------------
    url(r'^inspector$', views.mostrar_inspector, name="inspector"),
    url(r'^vista_de_inspecciones/(?P<pk_tramite>\d+)/$', views.ver_inspecciones, name="ver_inspecciones"),
    url(r'^cargar_inspeccion/(?P<pk_tramite>\d+)/$', views.cargar_inspeccion, name="cargar_inspeccion"),
    url(r'^agendar_tramite/(?P<pk_tramite>\d+)/$', views.agendar_tramite, name="agendar_tramite"),
    url(r'^rechazar_inspeccion/(?P<pk_tramite>\d+)/$', views.rechazar_inspeccion, name="rechazar_inspeccion"),
    url(r'^aceptar_inspeccion/(?P<pk_tramite>\d+)/$', views.aceptar_inspeccion, name="aceptar_inspeccion"),
    url(r'^documentos_tramite_inspector/(?P<pk_estado>\d+)/$', views.ver_documentos_tramite_inspector, name="documentos_tramite_inspector"),

    #jefeinspector --------------------------------------------------------------------------------------------------
    url(r'^jefeinspector$', views.mostrar_jefe_inspector, name="jefe_inspector"),
    url(r'^cargar_inspeccion_final/(?P<pk_tramite>\d+)/$', views.cargar_inspeccion_final, name="cargar_inspeccion_final"),
    url(r'^agendar_inspeccion_final/(?P<pk_tramite>\d+)/$', views.agendar_inspeccion_final, name="agendar_inspeccion_final"),
    url(r'^aceptar_inspeccion_final/(?P<pk_tramite>\d+)/$', views.aceptar_inspeccion_final, name="aceptar_inspeccion_final"),
    url(r'^inspectores_sin_inspecciones_agendadas/(?P<pk_estado>\d+)/$', views.inspectores_sin_inspecciones_agendadas, name="inspectores_sin_inspecciones_agendadas"),
    url(r'^documentos_tramite_jefeinspector/(?P<pk_estado>\d+)/$', views.ver_documentos_tramite_jefeinspector, name="documentos_tramite_jefeinspector"),
    url(r'^documentos_tramite_inspector_por_jefeinspector/(?P<pk_estado>\d+)/$', views.ver_documentos_tramite_inspector_por_jefeinspector, name="documentos_tramite_inspector_por_jefeinspector"),

    #director -------------------------------------------------------------------------------------------------------
    url(r'^director$', views.mostrar_director, name="director"),
    url(r'^vista_de_tramites$', views.ver_listado_todos_tramites, name="vista_de_tramites"),
    url(r'^detalle_de_tramite/(?P<pk_tramite>\d+)/$', views.detalle_de_tramite, name="detalle_de_tramite"),
    url(r'^reporte_tramites_director_excel/', ReporteTramitesDirectorExcel.as_view(), name="reporte_tramites_director_excel"),
    url(r'^reporte_tramites_director_pdf/$', login_required(ReporteTramitesDirectorPdf.as_view()), name="reporte_tramites_director_pdf"),
    url(r'^vista_de_usuarios$', views.ver_listado_todos_usuarios, name="vista_de_usuarios"),
    url(r'^ver_actividad_usuario/(?P<usuario>\w+)/$', views.ver_actividad_usuario, name="ver_actividad_usuario"),
    url(r'^visadores_sin_visado_agendado/(?P<pk_estado>\d+)/$', views.visadores_sin_visado_agendado, name="visadores_sin_visado_agendado"),
    url(r'^reporte_empleados_director_excel/', ReporteEmpleadosDirectorExcel.as_view(), name="reporte_empleados_director_excel"),
    url(r'^reporte_empleados_director_pdf/$', login_required(ReporteEmpleadosDirectorPdf.as_view()), name="reporte_empleados_director_pdf"),
    url(r'^ver_documentos_del_estado/(?P<pk_estado>\d+)/$', views.ver_documentos_del_estado, name="ver_documentos_del_estado"),

    #general ----------------------------------------------------------------------------------------------------
    url(r'^cambiar_perfil/$', views.cambiar_perfil, name="cambiar_perfil"),

]


