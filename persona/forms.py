from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Button
from crispy_forms.bootstrap import InlineField

from .models import *
from django.forms import ValidationError
from django.contrib.auth.forms import AuthenticationForm


class FormularioPersona(forms.ModelForm):
    class Meta:
        model = Persona
        fields = ('nombre', 'apellido', 'telefono', 'dni', 'domicilio', 'telefono', 'cuil')
    def __init__(self, *args, **kwargs):
        super(FormularioPersona, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('guardar_persona', 'Guardar'))


class FormularioProfesional(FormularioPersona):
    matricula = forms.CharField()
    categorias = forms.ChoiceField(choices=Profesional.CATEGORIAS)
    def __init__(self, *args, **kwargs):
        super(FormularioProfesional, self).__init__(*args, **kwargs)
        
    def save(self, commit=False):
        persona = super(FormularioProfesional,self).save(commit=commit)
        p = Profesional()
        p.save()
        persona.profesional= p
        persona.save()
        return p
    def clean_matricula(self):
        dato = self.cleaned_data.get['matricula']

        if dato == 1:
            raise ValidationError('matriula repetida')



class FormularioPropietario(forms.ModelForm):
    class Meta:
        model = Persona
        fields = ('nombre', 'apellido', 'telefono', 'dni', 'domicilio', 'telefono', 'cuil')

class FormularioUsuario(AuthenticationForm):

    def __init__(self, *args, **kwargs):
        super(FormularioUsuario, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout()
        self.helper.add_input(Submit('Submit', 'Submit', css_class='btn-default,'))

           


