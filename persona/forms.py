from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from .models import *

class FormularioPersona(forms.ModelForm):
    class Meta:
        model = Persona
        fields = ('nombre', 'apellido', 'telefono', 'dni', 'domicilio', 'telefono', 'cuil')
    def __init__(self, *args, **kwargs):
        super(FormularioPersona, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('guardar_persona', 'Guardar'))


class FormularioProfesional(forms.ModelForm):
    class Meta:
        model = Profesional
        fields = ('matricula', 'categoria')
    def __init__(self, *args, **kwargs):
        super(FormularioProfesional, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('Enviar Solicitud', 'Enviar Solicitud'))


class FormularioPropietario(forms.ModelForm):
    class Meta:
        model = Persona
        fields = ('nombre', 'apellido', 'telefono', 'dni', 'domicilio', 'telefono', 'cuil')

class FormularioUsuario(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ('username', 'password')
