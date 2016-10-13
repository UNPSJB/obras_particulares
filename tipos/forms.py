from django import forms

from .models import *

class FormularioTipoDocumento(forms.ModelForm):

    class Meta:
        model = TipoDocumento
        fields = ('nombre', 'descripcion', 'activo', 'fecha_alta')

class FormularioDocumento(forms.ModelForm):

    class Meta:
        model = Documento
        fields = ('identificador','tipoDocumento')

'''
class FormularioTipoObra(forms.ModelForm):

    class Meta:
        model = TipoObra
        fields = ('nombre','descripcion','categorias')
'''
