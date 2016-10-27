from django.conf.urls import include, url
from django.contrib import admin
from . import views

urlpatterns = [
    url(r'^login$', views.login, name='login'),
    url(r'^logout$', views.logout, name='logout'),
    url(r'^admin/', admin.site.urls),
    url(r'^persona/', include('persona.urls')),
    url(r'^tipos/', include('tipos.urls')),

]
