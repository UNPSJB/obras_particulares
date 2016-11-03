from django.conf.urls import include, url
from django.contrib.auth.decorators import login_required
from . import views


urlpatterns = [
    url(r'^alta$', views.alta_tramite, name="alta_tramite"),

 ]
