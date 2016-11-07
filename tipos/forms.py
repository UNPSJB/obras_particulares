from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from .models import *

class FormularioTipoDocumento(forms.ModelForm):
    NAME = 'tipo_documento_form'
    SUBMIT = 'tipo_documento_submit'
    class Meta:
        model = TipoDocumento
        fields = ('nombre', 'descripcion', 'activo', 'fecha_alta')

    def __init__(self, *args, **kwargs):
        super(FormularioTipoDocumento, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit(self.SUBMIT, 'Guardar'))

class FormularioDocumento(forms.ModelForm):
    NAME = 'documento_form'
    SUBMIT = 'documento_submit'
    class Meta:
        model = Documento
        fields = ('identificador','tipo_documento')

    def __init__(self, *args, **kwargs):
        super(FormularioDocumento, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('documento_submit', 'Guardar'))


class FormularioTipoObra(forms.ModelForm):
    NAME = 'tipo_obra_form'
    SUBMIT = 'tipo_obra_submit'
    class Meta:
        model = TipoObra
        fields = ('nombre','descripcion','categorias')

    def __init__(self, *args, **kwargs):
        super(FormularioTipoObra, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('tipo_obra_submit', 'Guardar'))
