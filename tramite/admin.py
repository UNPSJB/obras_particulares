from django.contrib import admin
from documento.models import Documento
from .models import *


class DocumentoInline(admin.TabularInline):
    model = Documento
    extra = 0
    min_num = 3

class TramiteAdmin(admin.ModelAdmin):
    pass
    '''inlines = [
        DocumentoInline
    ]'''

# Register your models here.
admin.site.register(Tramite, TramiteAdmin)
admin.site.register(Estado)
admin.site.register(Pago)
admin.site.register(Corregido)
admin.site.register(Aceptado)
admin.site.register(ConInspeccion)
admin.site.register(Iniciado)
admin.site.register(Visado)
admin.site.register(Inspeccionado)
admin.site.register(FinalObraSolicitado)
admin.site.register(Finalizado)
admin.site.register(Agendado)
