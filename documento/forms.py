from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout
from .models import *
from django.forms import ValidationError
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import Group, User

class FormularioDocumento(forms.ModelForm):
    NAME = 'documento_form'
    SUBMIT = 'documento_submit'
    class Meta:
        model = Documento
        fields = ('tramite','tipo_documento')

    def __init__(self, *args, **kwargs):
        super(FormularioDocumento, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        #self.helper.form_class = 'form-horizontal'
        self.helper.add_input(Submit('documento_submit', 'Guardar'))
