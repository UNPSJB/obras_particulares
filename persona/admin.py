from django.contrib import admin
from .models import *

class ALtaPersona(admin.ModelAdmin):
    _fieldsets = [
        ('Datos Persona', {'fields':['dni','nombre','apellido']}),
        ('Informacion general',{'fields':['mail','cuil','domicilio','telefono']}),
        ('ROLES', {'fields':['usuario', 'propietario', 'profesional']})
    ]

    search_fields = ['nombre','apellido','dni']
    list_display = ('apellido','nombre','dni','mail','cuil','domicilio','telefono')

class AltaProfesional(admin.ModelAdmin):
    _fieldsets = [
        ('Datos Profesional', {'fields':['matricula','categoria', 'profesion']}),
    ]
    search_fields = ['matricula','categoria' 'profesion']
    list_display = ('matricula','categoria', 'profesion')

admin.site.register(Persona,ALtaPersona)
admin.site.register(Profesional,AltaProfesional)
admin.site.register(Usuario)