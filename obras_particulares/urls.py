from django.conf.urls import include, url
from django.contrib import admin
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^login$', views.login_view, name='login'),
    url(r'^logout$', views.logout_view, name='logout'),
    url(r'^admin/', admin.site.urls),
    url(r'^persona/', include('persona.urls')),
    url(r'^tipos/', include('tipos.urls')),
    url(r'^tramite/', include('tramite.urls')),
    url(r'^documento/', include('documento.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
