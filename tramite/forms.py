from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout
from .models import *
from django.forms import ValidationError
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import Group, User

class FormularioTramite(forms.ModelForm):
    NAME = 'tramite_form'
    SUBMIT = 'tramite_submit'

    class Meta:
        model = Tramite
        fields = ('tipo_obra', 'medidas')

    def __init__(self, *args, **kwargs):
        super(FormularioTramite, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit(self.SUBMIT, 'Guardar Tramite'))

    def save(self, commit=False):

        tramite = super(FormularioTramite, self).save(commit=False)


        datos = self.cleaned_data
        propietario =  Propietario(
            dni = datos['dni'],
            nombre = datos['nombre'],
            apellido = datos['apellido'],
            cui = datos['cuil'],
            domicilio = datos['domicilio'],
            telefono = datos['telefono']
        )

        propietario.save()

        tramite.propietario = propietario

        return tramite



