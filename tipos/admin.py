from django.contrib import admin

# Register your models here.
from .models import *


class AltaTipoDocumento(admin.ModelAdmin):
    fieldsets = [
        ('Informacion general', {'fields':['nombre']}),
        (None,  {'fields':['descripcion']}),
        (None,  {'fields':['activo']}),
        ('Informacion de Fechas',{'fields':['fecha_alta']}),
        (None, {'fields':['fecha_baja']})
    ]



admin.site.register(TipoDocumento,AltaTipoDocumento)

admin.site.register(TipoObra)

admin.site.register(Documento)
