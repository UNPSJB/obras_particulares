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
        fields = ('nombre', 'descripcion', 'fecha_alta', 'requerido')

    def __init__(self, *args, **kwargs):
        super(FormularioTipoDocumento, self).__init__(*args, **kwargs)
        self.fields['nombre'].widget.attrs['title'] = "Ingresar Nombre"
        self.fields['nombre'].widget.attrs['pattern'] = "^[A-Za-z]{0,50}[A-Za-z0-9 ]{0,50}"
        self.fields['descripcion'].widget.attrs['title'] = "Ingresar Descripcion"
        self.fields['descripcion'].widget.attrs['pattern'] = "^[A-Za-z]{0,50}[A-Za-z0-9 ]{0,50}"
        self.fields['fecha_alta'].widget.attrs['title'] = "Ingresar Fecha de Alta"
        self.fields['requerido'] = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,
                                                             choices=TipoDocumento.ACCIONES)
        self.helper = FormHelper()
        self.helper.add_input(Submit(self.SUBMIT, 'Guardar'))
        self.helper.layout = Layout(
            Field('nombre', placeholder='Ingresar Nombre'),
            Field('descripcion', placeholder='Ingresar Descripcion'),
            Field('fecha_alta', placeholder='Ingresar Fecha de Alta', css_class='datepicker'),
            Field('requerido', placeholder="Ingresar una opcion")
        )

    def clean_requerido(self):
        flags = [int(e) for e in self.cleaned_data['requerido']]
        return sum(flags)


class FormularioTipoObra(forms.ModelForm):
    NAME = 'tipo_obra_form'
    SUBMIT = 'tipo_obra_submit'

    class Meta:
        model = TipoObra
        fields = ('nombre', 'valor_de_superficie', 'descripcion', 'categorias')

    def __init__(self, *args, **kwargs):
        super(FormularioTipoObra, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        # self.helper.form_class = 'form-horizontal'
        self.helper.add_input(Submit('tipo_obra_submit', 'Guardar'))
        self.fields['nombre'].widget.attrs['placeholder'] = "Ingresar Nombre"
        self.fields['nombre'].widget.attrs['pattern'] = "^[A-Za-z]{0,50}[A-Za-z0-9 ]{0,50}"
        self.fields['nombre'].widget.attrs['title'] = "Ingresar Nombre"
        self.fields['descripcion'].widget.attrs['placeholder'] = "Ingresar Descripcion"
        self.fields['descripcion'].widget.attrs['pattern'] = "^[A-Za-z]{0,50}[A-Za-z0-9 ]{0,50}"
        self.fields['descripcion'].widget.attrs['title'] = "Ingresar Descripcion"
        self.fields['categorias'].widget.attrs['title'] = "Ingresar Categoria"
        self.fields['valor_de_superficie'].widget.attrs['placeholder'] = "Ingresar Valor m2"
        self.fields['valor_de_superficie'].widget.attrs['max'] = "10000"
        self.fields['valor_de_superficie'].widget.attrs['min'] = "1"
        self.fields['valor_de_superficie'].widget.attrs['title'] = "Ingresar Valor m2"