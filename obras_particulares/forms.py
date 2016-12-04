from django.contrib.auth.forms import AuthenticationForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, ButtonHolder


class FormularioLogin(AuthenticationForm):

    def __init__(self, *args, **kwargs):
        super(FormularioLogin, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.fields['username'].widget.attrs['placeholder'] = "Ingresar Usuario"
        self.fields['username'].widget.attrs['title'] = "Ingresar Usuario"
        self.fields['password'].widget.attrs['placeholder'] = "Ingresar Contrasena"
        self.fields['password'].widget.attrs['title'] = "Ingresar Contrasena"

