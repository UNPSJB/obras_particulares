from django.db import models
from tipos.models import TipoDocumento
from tramite.models import Estado
from datetime import datetime

class Documento(models.Model):
    tipo_documento = models.ForeignKey(TipoDocumento)
    estado = models.ForeignKey(Estado, related_name='documentos')
    fecha = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to='documentos/%Y/%m/%d/',null=True,blank=True)

    def __str__(self):
        return self.tipo_documento.nombre
