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
    search_fields = ['nombre']
    list_display = ('nombre', 'descripcion')
    list_filter = ['fecha_alta']

class AltaDocumento(admin.ModelAdmin):
    fieldsets=[
        ('Informacion',{'fields':['identificador','tipoDocumento']}),
    ]
    search_fields=['identificador','tipoDocumento']

class AltaTipoObra(admin.ModelAdmin):
    fieldsets=[
        ('Informacion', {'fields':['nombre','descripcion','categorias']})
    ]
    search_fields = ['nombre']
    list_display = ('nombre', 'descripcion','categorias')


admin.site.register(TipoDocumento, AltaTipoDocumento)

admin.site.register(TipoObra, AltaTipoObra)

#admin.site.register(Documento, AltaDocumento)
