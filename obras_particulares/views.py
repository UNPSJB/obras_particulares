from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

class FormularioLogin(AuthenticationForm):

    def __init__(self, *args, **kwargs):
        super(FormularioLogin, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Submit', css_class="btn btn-default"))

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None and uFormularioUsuarioser.is_active :
            login(request, user)
            return redirect(user.get_view_name())
        else:
            messages.add_message(request, messages.WARNING, 'Clave o usuario incorrecto.')
    return redirect("home")

def logout_view(request):
    logout(request)
    return redirect("home")

def home(request):
    return render(request, 'home.html',
        {'login_usuario_form': FormularioLogin()})
