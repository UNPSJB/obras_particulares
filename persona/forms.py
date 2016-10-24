from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Button
from crispy_forms.bootstrap import InlineField

from .models import *
from django.contrib.auth.forms import AuthenticationForm


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

class FormularioUsuario(AuthenticationForm):

    def __init__(self, *args, **kwargs):
        super(FormularioUsuario, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-inline'
        self.helper.label_class = 'col-lg-6'
        self.helper.field_class = 'col-lg-6'
        self.helper.layout = Layout(

            'Nombre de usuario',
            'Contrasenia',
            'Recordarme',

        )
        self.helper.layout = Layout(
            self.helper.add_input(Submit('Sign in', 'ingresar', css_class='btn-default,'))
        )



class FormularioProfesional(forms.ModelForm):
    class Meta:
        model = Profesional
        fields = [
            'categoria',
            'matricula',
            'profesion',
        ]

        label = {
            'categoria': 'Categoria',
            'matricula': 'Matricula',
            'profesion': 'Profesion',

        }

        widgets = {
            'categoria': forms.TextInput(attrs={'class':'forms-control'}),
            'matricula': forms.TextInput(attrs={'class':'forms-control'}),
            'profesion': forms.TextInput(attrs={'class':'forms-control'}),
        }
