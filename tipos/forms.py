from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from .models import *

class FormularioTipoDocumento(forms.ModelForm):

    class Meta:
        model = TipoDocumento
        fields = ('nombre', 'descripcion', 'activo', 'fecha_alta')

    #Esto es para el crispy
    def __init__(self, *args, **kwargs):
        super(FormularioTipoDocumento, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        #self.helper.form_class = 'form-horizontal'
        self.helper.add_input(Submit('guardar_tipo_documento', 'Guardar'))

class FormularioDocumento(forms.ModelForm):

    class Meta:
        model = Documento
        fields = ('identificador','tipo_documento')

    def __init__(self, *args, **kwargs):
        super(FormularioDocumento, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        #self.helper.form_class = 'form-horizontal'
        self.helper.add_input(Submit('submit', 'Guardar'))


class FormularioTipoObra(forms.ModelForm):

    class Meta:
        model = TipoObra
        fields = ('nombre','descripcion','categorias')

    def __init__(self, *args, **kwargs):
        super(FormularioTipoObra, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        #self.helper.form_class = 'form-horizontal'
        self.helper.add_input(Submit('guardar_tipo_de_obra', 'Guardar'))
