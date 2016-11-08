from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout
from .models import *
from django.forms import ValidationError
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import Group, User

class FormularioPersona(forms.ModelForm):
    NAME = 'persona_form'
    SUBMIT = 'persona_submit'

    class Meta:
        model = Persona
        fields = ('nombre', 'apellido', 'telefono', 'dni', 'domicilio', 'telefono', 'cuil', 'mail')

    def __init__(self, *args, **kwargs):
        super(FormularioPersona, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit(self.SUBMIT, 'Guardar'))

class FormularioProfesional(FormularioPersona):
    NAME = 'profesional_form'
    SUBMIT = 'profesional_submit'
    matricula = forms.CharField()
    profesion =forms.CharField()
    categorias = forms.ChoiceField(choices=Profesional.CATEGORIAS)
    certificado = forms.ImageField()

    def __init__(self, *args, **kwargs):
        super(FormularioProfesional, self).__init__(*args, **kwargs)

    def save(self, commit=False):
        persona = super(FormularioProfesional,self).save(commit=commit)
        datos = self.cleaned_data
        p = Profesional(
            profesion= datos['profesion'],
            matricula= datos['matricula'],
            categoria= datos['categorias'],
            certificado = datos['certificado'])
        p.save()
        persona.profesional= p
        persona.save()
        return p

    def clean_matricula(self):
        dato = self.cleaned_data['matricula']
        if Profesional.objects.filter(matricula=dato).exists():
            raise ValidationError('Matricula repetida')
        return dato

class FormularioPropietario(forms.ModelForm):
    NAME = 'propietario_form'
    SUBMIT = 'propietario_submit'

    class Meta:
        model = Persona
        fields = ('nombre', 'apellido', 'telefono', 'dni', 'domicilio', 'telefono', 'cuil')

class FormularioUsuario(AuthenticationForm):
    NAME = 'usuario_form'
    SUBMIT = 'usuario_submit'

    def __init__(self, *args, **kwargs):
        super(FormularioUsuario, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Submit', css_class="btn btn-default"))


class FormularioUsuarioPersona(FormularioPersona):
    NAME = 'usuario_persona_form'
    SUBMIT = 'usuario_persona_submit'
    usuario = forms.CharField()
    password = forms.CharField()

    def __init__(self, *args, **kwargs):
        super(FormularioUsuarioPersona, self).__init__(*args, **kwargs)

    def save(self, commit = False):
        persona = super(FormularioUsuarioPersona, self).save(commit = False)
        datos = self.cleaned_data
        persona.usuario = Usuario.objects.create_user(username = datos['usuario'],
                                                      email = datos['mail'],
                                                      password = datos['password'],)
        persona.usuario.save()
        persona.save()
        return persona.usuario


class FormularioAdministrativo(FormularioUsuarioPersona):
    NAME = 'administrativo_form'
    SUBMIT = 'administrativo_submit'

    def save(self, commit=False):
        usuario = super(FormularioAdministrativo, self).save(commit=False)
        grupo = Group.objects.get(name='administrativo')
        usuario.groups.add(grupo)
        return usuario

class FormularioVisador(FormularioUsuarioPersona):
    NAME = 'visador_form'
    SUBMIT = 'visador_submit'

    def save(self, commit = False):
        usuario = super(FormularioVisador, self).save(commit=False)
        grupo = Group.objects.get(name = 'visador')
        usuario.groups.add(grupo)
        return usuario

class FormularioInspector(FormularioUsuarioPersona):
    NAME = 'inspector_form'
    SUBMIT = 'inspector_submit'

    def save(self, commit = False):
        usuario = super(FormularioInspector, self).save(commit=False)
        grupo = Group.objects.get(name='inspector')
        usuario.groups.add(grupo)
        return usuario

class FormularioBusquedaPropietario(forms.Form):
    NAME = 'busqueda_propietario_form'
    SUBMIT = 'busqueda_propietario_submit'
    dni = forms.CharField()

    def __init__(self, *args, **kwargs):
        super(FormularioBusquedaPropietario, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit(self.SUBMIT, 'Buscar Propietario'))

    def clean_dni(self):
        print("Entre al clean")
        dato = self.cleaned_data['dni']
        if Propietario.objects.filter(dni=dato).exists():
            raise ValidationError('El propietario ya existe')

        return dato


