from django.conf.urls import include, url
from . import views


urlpatterns = [
    url(r'^tipoDocumento/new/$', views.alta_tipoDocumento),
    url(r'^tipoDocumento$', views.mostrar_tipoDocumento, name='mostrar_tipoDocumento'),
    url(r'^tipoObra/new/$', views.alta_tipoObra, name='alta_tipoObra'),
    url(r'^documento/new/$', views.alta_documento, name='alta_docuemto'),
]
