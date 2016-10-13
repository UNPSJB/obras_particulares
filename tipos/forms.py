from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from .models import *

class FormularioTipoDocumento(forms.ModelForm):

    class Meta:
        model = TipoDocumento
        fields = ('nombre', 'descripcion', 'activo', 'fecha_alta')

    #Esto es pora el crispy
    def __init__(self, *args, **kwargs):
        super(FormularioTipoDocumento, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        #self.helper.form_class = 'form-horizontal'
        self.helper.add_input(Submit('submit', 'Submit'))

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
