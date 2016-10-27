from django.conf.urls import include, url
from django.contrib import admin
from . import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^login$', views.login_view, name='login'),
    url(r'^logout$', views.logout_view, name='logout'),
    url(r'^admin/', admin.site.urls),
    url(r'^persona/', include('persona.urls')),
    url(r'^tipos/', include('tipos.urls')),

]
