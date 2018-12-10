from django.conf.urls import include, url
from django.contrib import admin
from . import views


urlpatterns = [
    url(r'^alta/$', views.alta_documento, name='alta_docuemto'),

    #Documentacion
    url(r'^documentacion/$', views.documentation),
    url(r'^documentacion/(?P<path>.*)$', views.documentation, name="manual"),
    url(r'^documentacion_indice/(?P<path>.*)$', views.documentacion_indice, name="manual_indice")
]
