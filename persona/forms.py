from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, ButtonHolder
from django.contrib.admin.helpers import Fieldset

from .models import *
from tramite.models import *
from django.forms import ValidationError
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import Group, User

class FormularioPersona(forms.ModelForm):
    NAME = 'persona_form'
    SUBMIT = 'persona_submit'

    class Meta:
        model = Persona
        fields = ('dni', 'nombre', 'apellido', 'telefono', 'domicilio', 'cuil', 'mail')

    def __init__(self, *args, **kwargs):
        super(FormularioPersona, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit(self.SUBMIT, 'Enviar Solicitud'))
        #self.helper.form_tag = False
        for field_name in self.fields:
            field = self.fields.get(field_name)
            if field:
                if type(field.widget) in (forms.TextInput, forms.DateInput):
                    field.widget = forms.TextInput(attrs={'placeholder': "Ingresar " + str(field.label)})

        self.fields['mail'].widget.attrs['placeholder'] = "Ingresar Mail"
        self.fields['dni'].widget.attrs['placeholder'] = "Ingresar Dni"
        self.fields['dni'].widget.attrs['max'] = "99999999"
        self.fields['dni'].widget.attrs['min'] = "9999999"
        self.fields['cuil'].widget.attrs['pattern'] = "^[0-9]{2}-[0-9]{8}/[0-9]$"
        self.fields['cuil'].widget.attrs['title'] = "Ingresar un cuil con el formato xx-xxxxxxxx/x"
        self.fields['cuil'].widget.attrs['placeholder'] = "Ingresar Cuil - Formato: xx-xxxxxxxx/x"

    def clean_dni(self):
        dato = self.cleaned_data['dni']
        if Persona.objects.filter(dni=dato).exists():
            raise ValidationError('La persona ya existe en el sistema')
        return dato

class FormularioProfesional(FormularioPersona):
    NAME = 'profesional_form'
    SUBMIT = 'profesional_submit'
    matricula = forms.CharField()
    profesion = forms.CharField()
    categorias = forms.ChoiceField(choices=Profesional.CATEGORIAS)
    certificado = forms.ImageField()

    def __init__(self, *args, **kwargs):
        super(FormularioProfesional, self).__init__(*args, **kwargs)
        self.fields['matricula'].widget.attrs['placeholder'] = "Ingresar Matricula"
        self.fields['profesion'].widget.attrs['placeholder'] = "Ingresar Profesion"

    def save(self, commit=False):
        persona = super(FormularioProfesional, self).save(commit=commit)
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

class FormularioPropietario(FormularioPersona):
    NAME = 'propietario_form'
    SUBMIT = 'propietario_submit'

    def __init__(self, *args, **kwargs):
        super(FormularioPropietario, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False

    def save(self, commit=False):
        persona = super(FormularioPropietario, self).save(commit=commit)
        p = Propietario()
        p.save()
        persona.propietario = p
        persona.save()
        return p

    def obtener_o_crear(self, persona=None):
        if persona:
            if persona.propietario:
                return persona.propietario
            else:
                 propietario = Propietario()
                 propietario.save()
                 persona.propietario = propietario
                 persona.save()
                 return persona.propietario

        elif self.is_valid():
            return self.save()

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

    #ver como armo esto automaticamente y como lo saco fuera para que todos lo conoscan, lo uso mas abajo

    grupos = {
        ('1', 'director'),
        ('2', 'administrativo'),
        ('3', 'visador'),
        ('4', 'inspector'),
        ('7', 'jefeinspector')}

    grupo = forms.TypedMultipleChoiceField(grupos)

    def __init__(self, *args, **kwargs):
        super(FormularioUsuarioPersona, self).__init__(*args, **kwargs)
        self.fields['usuario'].widget.attrs['placeholder'] = "Ingresar Nombre Usuario"
        self.fields['usuario'].widget.attrs['pattern'] = ".{5,}"
        self.fields['password'].widget.attrs['placeholder'] = "Ingresar Contrasena"
        self.fields['password'].widget.attrs['pattern'] = ".{6,}"

    def save(self, commit=False):
        persona = super(FormularioUsuarioPersona, self).save(commit=False)
        datos = self.cleaned_data
        persona.usuario = Usuario.objects.create_user(username=datos['usuario'],
                                                      email=datos['mail'],
                                                      password=datos['password'],
                                                      )

        grupos = {
            ('1', 'director'),
            ('2', 'administrativo'),
            ('3', 'visador'),
            ('4', 'inspector'),
            ('7', 'jefeinspector')}

        grupo_post = datos['grupo']

        for g in grupos:
            for gp in grupo_post:
                if g[0] == gp:
                    persona.usuario.save()
                    persona.save()
                    usuario = persona.usuario
                    usuario.groups.add(gp)
        return usuario


class FormularioArchivoPago(forms.Form):

    NAME = 'archivo_pago_form'
    SUBMIT = 'archivo_pago_submit'
    pagos = forms.FileField()

    class Meta:
        fields= ('file', 'pagos')

    def __init__(self, *args, **kwargs):
        super(FormularioArchivoPago, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Submit', css_class="btn btn-default"))

