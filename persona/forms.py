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
        #self.helper.form_class = 'form-horizontal'
        self.helper.add_input(Submit('submit', 'Guardar'))


class FormularioProfesional(forms.ModelForm):

    class Meta:
        model = Profesional
        fields = ('matricula', 'categoria') #'profesion'


class FormularioPropietario(forms.ModelForm):

    class Meta:
        model = Persona
        fields = ('nombre', 'apellido', 'telefono', 'dni', 'domicilio', 'telefono', 'cuil')

''' SE DEBE PARSEAR CON LOS ROLES?

class FormularioUsuaro(forms.ModelForm):

    class Meta:
        fields = ('nombre_de_usuario')
'''
