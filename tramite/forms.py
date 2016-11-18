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
        self.helper.form_tag = False


    '''def clean_propietario(self, commi=False):
        dni = self.cleaned_data['propietario']
        if not Persona.objects.filter(dni=dni).exists() :
            raise ValidationError('El propietario no existe. Cargalo!!')

        persona = Persona.objects.get(dni=dni)
        if not (persona.propietario):
            raise ValidationError('La persona ingresada no es propietario registrado')
        return dni'''

    def save(self, commit=True, propietario=None):
        tramite = super(FormularioIniciarTramite, self).save(commit=False)
        if propietario is not None:
            tramite.propietario = propietario
        if commit:
            tramite.save()
        return tramite
