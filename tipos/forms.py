from django import forms
from crispy_forms.helper import FormHelper, Layout
from crispy_forms.layout import Submit, Field
import datetime

from .models import *
from documento import *
from tipos import *

class FormularioTipoDocumento(forms.ModelForm):
    NAME = 'tipo_documento_form'
    SUBMIT = 'tipo_documento_submit'
    class Meta:
        model = TipoDocumento
        fields = ('nombre', 'descripcion', 'activo', 'fecha_alta', 'requerido')

    #Esto es para el crispy
    def __init__(self, *args, **kwargs):
        super(FormularioTipoDocumento, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        #self.helper.form_class = 'form-horizontal'
        self.helper.add_input(Submit(self.SUBMIT, 'Guardar'))
        self.helper.layout = Layout(
            Field('nombre', placeholder='Nombre'),
            Field('descripcion', placeholder='Descripcion'),
            Field('activo', placeholder='Activo'),
            Field('fecha_alta', placeholder='Fecha alta', css_class='datepicker'),
            Field('requerido', placeholder='requerido'),
        )
        self.fields['requerido'] = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,
                                                             choices=TipoDocumento.ACCIONES)
        

    def clean_requerido(self):
        flags = [int(e) for e in self.cleaned_data['requerido']]
        return sum(flags)

class FormularioTipoObra(forms.ModelForm):
    NAME = 'tipo_obra_form'
    SUBMIT = 'tipo_obra_submit'
    class Meta:
        model = TipoObra
        fields = ('nombre','descripcion','categorias')

    def __init__(self, *args, **kwargs):
        super(FormularioTipoObra, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        #self.helper.form_class = 'form-horizontal'
        self.helper.add_input(Submit('tipo_obra_submit', 'Guardar'))
