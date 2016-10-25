from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from .models import *
from django.forms import ValidationError

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
    profesion =forms.CharField()
    categorias = forms.ChoiceField(choices=Profesional.CATEGORIAS)
    def __init__(self, *args, **kwargs):
        super(FormularioProfesional, self).__init__(*args, **kwargs)

    def save(self, commit=False):
        persona = super(FormularioProfesional,self).save(commit=commit)
        datos = self.cleaned_data
        p = Profesional(
            profesion= datos['profesion'],
            matricula= datos['matricula'],
            categoria= datos['categorias'],
        )
        p.save()
        persona.profesional= p
        persona.save()
        return p

    def clean_matricula(self):
        dato = self.cleaned_data['matricula']
        if Profesional.objects.filter(matricula=dato).exists():
            raise ValidationError('matricula repetida')
        return dato
                
class FormularioPropietario(forms.ModelForm):
    class Meta:
        model = Persona
        fields = ('nombre', 'apellido', 'telefono', 'dni', 'domicilio', 'telefono', 'cuil')

class FormularioUsuario(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ('username', 'password')
    def __init__(self, *args, **kwargs):
        super(FormularioUsuario, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        #self.helper.form_class = 'form-horizontal'
        self.helper.add_input(Submit('guardar_usuario', 'Guardar'))

