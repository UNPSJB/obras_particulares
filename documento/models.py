from django.db import models
from tipos.models import TipoDocumento
from tramite.models import Tramite
from datetime import datetime

class Documento(models.Model):
    tipo_documento = models.ForeignKey(TipoDocumento)
    tramite = models.ForeignKey(Tramite,related_name='documentos')
    fecha = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return self.tipo_documento.nombre
