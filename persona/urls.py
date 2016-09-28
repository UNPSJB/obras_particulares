from django.conf.urls import include, url
from . import views


urlpatterns = [

    url(r'^inicio$', views.mostrar_inicio),
    url(r'^inspector$', views.mostrar_inspector),
    url(r'^profesional$', views.mostrar_profesional),
    url(r'^jefeinspector$', views.mostrar_jefe_inspector),
]