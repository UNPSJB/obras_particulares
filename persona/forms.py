from django import forms

from .models import *

class FormularioPersona(forms.ModelForm):

    class Meta:
        model = Persona
        fields = ('Nombre', 'Apellido', 'Dni', 'Direccion', 'Telefono', 'cuil')