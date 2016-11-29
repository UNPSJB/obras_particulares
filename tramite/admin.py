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
