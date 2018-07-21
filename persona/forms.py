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

        self.fields['dni'].widget.attrs['placeholder'] = "Ingresar Dni"
        self.fields['dni'].widget.attrs['max'] = "99999999"
        self.fields['dni'].widget.attrs['min'] = "9999999"
        self.fields['dni'].widget.attrs['title'] = "Ingresar Nro de documento"
        self.fields['cuil'].widget.attrs['pattern'] = "^[0-9]{2}-[0-9]{8}/[0-9]$"
        self.fields['cuil'].widget.attrs['title'] = "Ingresar Cuil con formato xx-xxxxxxxx/x"
        self.fields['cuil'].widget.attrs['placeholder'] = "Ingresar Cuil - Formato: xx-xxxxxxxx/x"
        self.fields['nombre'].widget.attrs['title'] = "Ingresar Nombre"
        self.fields['nombre'].widget.attrs['pattern'] = "^[A-Za-z]{0,50}[A-Za-z ]{0,50}"
        self.fields['apellido'].widget.attrs['title'] = "Ingresar Apellido"
        self.fields['apellido'].widget.attrs['pattern'] = "^[A-Za-z]{0,50}[A-Za-z ]{0,50}"
        self.fields['telefono'].widget.attrs['title'] = "Ingresar Nro de Telefono"
        self.fields['telefono'].widget.attrs['pattern'] = "^[0-9]{0,15}"
        self.fields['domicilio'].widget.attrs['title'] = "Ingresar Domicilio"
        self.fields['domicilio'].widget.attrs['pattern'] = "^[A-Za-z]{0,50}[A-Za-z ]{0,50} [0-9]{0,5}$"
        self.fields['mail'].widget.attrs['title'] = "Ingresar Mail"
        self.fields['mail'].widget.attrs['placeholder'] = "Ingresar Mail - Formato: xxxxxxx@xxx.xxx"

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
        self.fields['matricula'].widget.attrs['title'] = "Ingresar Nro de Matricula"
        self.fields['profesion'].widget.attrs['title'] = "Ingresar Profesion"

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

    gruposEmp = set()
    valor= 1
    for g in Group.objects.all():
        e = Group.objects.select_related().get(id=valor)
        if str(e) <> 'propietario' and str(e) <> 'profesional':
            gruposEmp.add((str(valor), str(e)))
        valor += 1
    grupo = forms.TypedMultipleChoiceField(gruposEmp)

    def __init__(self, *args, **kwargs):
        super(FormularioUsuarioPersona, self).__init__(*args, **kwargs)
        self.fields['usuario'].widget.attrs['placeholder'] = "Ingresar Nombre Usuario"
        self.fields['usuario'].widget.attrs['pattern'] = ".{5,}"
        self.fields['password'].widget.attrs['placeholder'] = "Ingresar Contrasena"
        self.fields['password'].widget.attrs['pattern'] = ".{6,}"
        self.fields['usuario'].widget.attrs['title'] = "Ingresar Usuario"
        self.fields['password'].widget.attrs['title'] = "Ingresar Contrasena"

    def save(self, commit=False):
        persona = super(FormularioUsuarioPersona, self).save(commit=False)
        datos = self.cleaned_data
        persona.usuario = Usuario.objects.create_user(username=datos['usuario'], email=datos['mail'], password=datos['password'],)

        grupo_post = datos['grupo']

        for g in self.gruposEmp:
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
        self.helper.add_input(Submit('submit', 'Enviar', css_class="btn btn-default"))

class FormularioUsuarioGrupo(forms.Form):
    NAME = 'usuario_grupo_form'
    SUBMIT = 'usuario_grupo_submit'
    usuario_seleccionado = forms.CharField()
    gruposEmp = set()
    valor = 1
    for g in Group.objects.all():
        e = Group.objects.select_related().get(id=valor)
        if str(e) <> 'propietario' and str(e) <> 'profesional':
            gruposEmp.add((str(valor), str(e)))
        valor += 1
    grupos_disponibles = forms.TypedMultipleChoiceField(gruposEmp)

    def __init__(self, *args, **kwargs):
        super(FormularioUsuarioGrupo, self).__init__(*args, **kwargs)
        self.fields['usuario_seleccionado'].widget.attrs['placeholder'] = "Ingresar Nombre Usuario"
        self.fields['usuario_seleccionado'].widget.attrs['title'] = "Ingresar Usuario"
        self.helper = FormHelper()
        self.helper.add_input(Submit('usuario_grupo_submit', 'Modificar grupo', css_class="btn btn-default"))

    def save(self, commit=False):
        datos = self.cleaned_data
        userSel = Usuario.objects.get(username=datos['usuario_seleccionado'])
        grupo_post = list(datos['grupos_disponibles'])
        for g in self.gruposEmp:
            if g[0] == grupo_post[0]:
                u = userSel.persona.modificarGrupo(g[1])
        return u

class FormularioUsuarioCambiarDatos(forms.Form):
    NAME = 'usuario_datospersonales_form'
    SUBMIT = 'usuario_datospersonales_submit'

    mail_usuario = forms.EmailField(max_length=40, required=False)
    domicilio_usuario = forms.CharField(max_length=50, required=False)
    telefono_usuario = forms.CharField(max_length=15, required=False)
    usuario_nombre = forms.CharField()
    cambiar_foto_de_perfil = forms.ImageField(required=False)

    def __init__(self, *args, **kwargs):
        super(FormularioUsuarioCambiarDatos, self).__init__(*args, **kwargs)
        self.fields['usuario_nombre'].widget.attrs['placeholder'] = "Ingresar Nombre Usuario"
        self.fields['usuario_nombre'].widget.attrs['pattern'] = ".{5,}"
        self.fields['usuario_nombre'].widget.attrs['title'] = "Ingresar Usuario"
        self.fields['telefono_usuario'].widget.attrs['title'] = "Ingresar Nro de Telefono"
        self.fields['telefono_usuario'].widget.attrs['pattern'] = "^[0-9]{0,15}"
        self.fields['telefono_usuario'].widget.attrs['placeholder'] = "Ingresar Nro de Telefono"
        self.fields['domicilio_usuario'].widget.attrs['title'] = "Ingresar Domicilio"
        self.fields['domicilio_usuario'].widget.attrs['pattern'] = "^[A-Za-z]{0,50}[A-Za-z ]{0,50} [0-9]{0,5}$"
        self.fields['domicilio_usuario'].widget.attrs['placeholder'] = "Ingresar Domicilio"
        self.fields['mail_usuario'].widget.attrs['title'] = "Ingresar Mail"
        self.fields['mail_usuario'].widget.attrs['placeholder'] = "Ingresar Mail - Formato: xxxxxxx@xxx.xxx"
        self.helper = FormHelper()
        self.helper.add_input(Submit('usuario_datospersonales_submit', 'Modificar mis datos', css_class="btn btn-default"))

    def save(self, commit=False):
        datos = self.cleaned_data
        u = Usuario.objects.get(username=datos['usuario_nombre'])
        u.persona.modificarUsuario(datos['mail_usuario'], datos['domicilio_usuario'], datos['telefono_usuario'], datos['cambiar_foto_de_perfil'])
        return u

class FormularioUsuarioContrasenia(forms.Form):
    NAME = 'usuario_contrasenia_form'
    SUBMIT = 'usuario_contrasenia_submit'
    #"""
    #A form that lets a user change set their password without entering the old
    #password
    #"""
    error_messages = {
        'password_mismatch': ("Los dos campos de contrasena no coinciden."),
    }
    usuario_nombre1 = forms.CharField(label=("Nombre de usuario"))
    new_password1 = forms.CharField(label=("Nuevo password"),widget=forms.PasswordInput)
    new_password2 = forms.CharField(label=("Confirmar nuevo password"),widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super(FormularioUsuarioContrasenia, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(
        Submit('usuario_contrasenia_submit', 'Modificar password', css_class="btn btn-default"))

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(
                    self.error_messages['password_mismatch'],
                    code='password_mismatch',
                )
        return password2

    def save(self, commit=True):
        u = Usuario.objects.get(username=self.cleaned_data['usuario_nombre1'])
        u.set_password(self.cleaned_data['new_password1'])
        if commit:
            u.save()
        return u
