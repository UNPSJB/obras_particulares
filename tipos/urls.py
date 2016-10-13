from django.conf.urls import include, url
from . import views


urlpatterns = [
    url(r'^alta_tipoDocumento/new/$', views.alta_tipoDocumento),
    url(r'^tipoDocumento$', views.mostrar_tipoDocumento,name='mostrar_tipoDocumento'),
]
