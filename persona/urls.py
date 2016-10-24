from django.conf.urls import include, url
from . import views


urlpatterns = [

    url(r'^inicio$', views.mostrar_inicio),
    url(r'^index$', views.mostrar_index),
    url(r'^inspector$', views.mostrar_inspector),
    url(r'^jefeinspector$', views.mostrar_jefe_inspector),
    url(r'^propietario$', views.mostrar_propietario,name='mostrar_propietario'),
    url(r'^visador$', views.mostrar_visador),
    url(r'^visar$', views.mostrar_visar),
    url(r'^altapersona$', views.alta_persona),
    url(r'^director$', views.mostrar_director),
    url(r'^administrativo$', views.profesional_list),
    url(r'^nuevoprofesional$', views.nuevo),

]
