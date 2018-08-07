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


admin.site.register(Iniciado)
admin.site.register(Aceptado)
admin.site.register(AgendadoParaVisado)
admin.site.register(Visado)
admin.site.register(AgendadoPrimerInspeccion)
admin.site.register(PrimerInspeccion)
admin.site.register(AprobadoSolicitado)
admin.site.register(Aprobado)
admin.site.register(NoAprobadoSolicitado)
admin.site.register(NoAprobado)
admin.site.register(AprobadoSolicitadoPorPropietario)
admin.site.register(AprobadoPorPropietario)
admin.site.register(AgendadoInspeccion)
admin.site.register(Inspeccionado)
admin.site.register(FinalObraTotalSolicitado)
admin.site.register(AgendadoInspeccionFinal)
admin.site.register(InspeccionFinal)
admin.site.register(Finalizado)
admin.site.register(FinalObraParcialSolicitado)
admin.site.register(Baja)
