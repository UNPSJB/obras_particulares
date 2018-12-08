from django import forms
from django.forms import ValidationError
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout
from .models import *

class FormularioIniciarTramite(forms.ModelForm):
    NAME = 'tramite_form'
    SUBMIT = 'tramite_submit'
    propietario = forms.CharField(label="Dni propietario")

    class Meta:
        model = Tramite
        fields = ('tipo_obra', 'medidas', 'profesional','domicilio', 'destino_obra')
        widgets = {
            "profesional": forms.HiddenInput()
        }

    def __init__(self, *args, **kwargs):
        super(FormularioIniciarTramite, self).__init__(*args, **kwargs)
        for field_name in self.fields:
            field = self.fields.get(field_name)
            if field:
                if type(field.widget) in (forms.TextInput, forms.DateInput):
                    field.widget = forms.TextInput(attrs={'placeholder': "Ingresar " + str(field.label)})
        self.fields['tipo_obra'].widget.attrs['placeholder'] = "Ingresar Tipo de Obra"
        self.fields['tipo_obra'].widget.attrs['title'] = "Ingresar Tipo de Obra"
        self.fields['medidas'].widget.attrs['placeholder'] = "Ingresar Medidas en m2"
        self.fields['medidas'].widget.attrs['title'] = "Ingresar Medidas en m2"
        self.fields['medidas'].widget.attrs['max'] = "10000"
        self.fields['medidas'].widget.attrs['min'] = "1"
        self.fields['propietario'].widget.attrs['placeholder'] = "Ingresar DNI del Propietario"
        self.fields['propietario'].widget.attrs['title'] = "Ingresar DNI del Propietario"
        self.fields['propietario'].widget.attrs['max'] = "99999999"
        self.fields['propietario'].widget.attrs['min'] = "9999999"
        self.fields['domicilio'].widget.attrs['placeholder'] = "Ingresar Domicilio de la Obra"
        self.fields['domicilio'].widget.attrs['title'] = "Ingresar Domicilio de la Obra"
        #self.fields['domicilio'].widget.attrs['pattern'] = "^[A-Za-z]{0,50}[A-Za-z ]{0,50} [0-9]{0,5}$"


    def save(self, commit=True, propietario=None):
        tramite = super(FormularioIniciarTramite, self).save(commit=False)
        if propietario is not None:
            tramite.propietario = propietario
        if commit:
            tramite.save()
        return tramite
