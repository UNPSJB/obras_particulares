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
        self.helper.add_input(Submit('guardar_persona', 'Guardar'))


class FormularioProfesional(forms.ModelForm):

    class Meta:
        model = Profesional
        fields = ('matricula', 'categoria') #'profesion'


class FormularioPropietario(forms.ModelForm):

    class Meta:
        model = Persona
        fields = ('nombre', 'apellido', 'telefono', 'dni', 'domicilio', 'telefono', 'cuil')



class FormularioUsuario(forms.ModelForm):

    class Meta:
        model = Usuario
        fields = ('nombre_de_usuario', 'contrasenia')

    def __init__(self, *args, **kwargs):
        super(FormularioUsuario, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        #self.helper.form_class = 'form-horizontal'
        self.helper.add_input(Submit('guardar_usuario', 'Guardar'))

