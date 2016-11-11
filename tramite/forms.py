from django import forms
from django.forms import ValidationError
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout
from .models import *

class FormularioIniciarTramite(forms.ModelForm):
    NAME = 'tramite_form'
    SUBMIT = 'tramite_submit'
    propietario = forms.CharField()

    class Meta:
        model = Tramite
        fields = ('tipo_obra', 'medidas', 'profesional')
        widgets = {
            "profesional": forms.HiddenInput()
        }

    def __init__(self, *args, **kwargs):
        super(FormularioIniciarTramite, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit(self.SUBMIT, 'Guardar Tramite'))

    def clean_propietario(self):
        dato = self.cleaned_data['propietario']
        propitario = Propietario.objects.filter(dni=dato).first()
        if propitario is None:
            raise ValidationError('La persona no existe en el sistema, debe crearla')
        return propitario

    def save(self, commit=False):
        tramite = super(FormularioIniciarTramite, self).save(commit=False)
        datos = self.cleaned_data
        propietario = Propietario(
            dni = datos['dni'],
            nombre = datos['nombre'],
            apellido = datos['apellido'],
            cui = datos['cuil'],
            domicilio = datos['domicilio'],
            telefono = datos['telefono']
        )

        propietario.save()
        tramite.propietario = propietari
        return tramite
