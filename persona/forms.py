from django import forms

from .models import *

class FormularioPersona(forms.ModelForm):

    class Meta:
        model = Persona
        fields = ('nombre', 'apellido', 'telefono', 'dni', 'domicilio', 'telefono', 'cuil')


class FormularioProfesional(forms.ModelForm):

    class Meta:
        model = Profesional
        fields = ('matricula', 'profesion', 'categoria')


class FormularioPropietario(forms.ModelForm):

    class Meta:
        model = Persona

class FormularioUsuaro(forms.ModelForm):

    class Meta:
        fields = ('nombre_de_usuario')
