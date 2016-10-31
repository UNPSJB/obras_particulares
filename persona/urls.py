from django.conf.urls import include, url
from django.contrib.auth.decorators import login_required
from . import views


urlpatterns = [

    url(r'^index$', views.mostrar_index,name="index"),
    url(r'^inspector$', views.mostrar_inspector,name="inspector"),
    url(r'^jefeinspector$', views.mostrar_jefe_inspector,name="jefe_inspector"),
    url(r'^propietario$', views.mostrar_propietario,name="propietario"),
    url(r'^visador$', views.mostrar_visador,name="visador"),
    url(r'^visar$', views.mostrar_visar,name="visar"),
    url(r'^altapersona$', views.alta_persona,name="alta_persona"),
    url(r'^director$', views.mostrar_director,name="director"),
    url(r'^administrativo$', views.mostrar_administrativo,name="administrativo"),
    url(r'^nuevoprofesional$', views.nuevo,name="nuevo_profesional"),

]
