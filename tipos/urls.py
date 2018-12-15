from django.conf.urls import include, url
from . import views

urlpatterns = [
    url(r'^tipoDocumento/new/$', views.alta_tipoDocumento),
    url(r'^tipoDocumento$', views.mostrar_tipoDocumento, name='mostrar_tipoDocumento'),
    url(r'^tipoObra/new/$', views.alta_tipoObra, name='alta_tipoObra'),
    url(r'^tipoDocumento/activar/(?P<pk_tipo_documento>\d+)/$', views.activar, name='activar_tipo_documento'),
    url(r'^tipoDocumento/desactivar/(?P<pk_tipo_documento>\d+)/$', views.desactivar, name='desactivar_tipo_documento')

]

