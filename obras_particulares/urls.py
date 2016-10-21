from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'', include('persona.urls')),
    url(r'', include('tipos.urls')),

]
