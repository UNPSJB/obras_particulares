from django.contrib import admin
from .models import *

class ALtaPersona(admin.ModelAdmin):
    fieldsets = [
        ('Datos Persona', {'fields':['dni','nombre','apellido']}),
        ('Informacion general',{'fields':['mail','cuil','domicilio','telefono']}),
    ]

    search_fields = ['nombre','apellido','dni']
    list_display = ('apellido','nombre','dni','mail','cuil','domicilio','telefono')


admin.site.register(Persona,ALtaPersona)
admin.site.register(Propietario)
admin.site.register(Usuario)
admin.site.register(Profesional)
