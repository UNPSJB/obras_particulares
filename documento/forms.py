from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout
from .models import *
from django.forms import BaseFormSet
from django.forms import formset_factory
from documento.models import *

class FormularioCorreccionesDocumento(forms.Form):
    file_field = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))


class FormularioDocumento(forms.ModelForm):
    '''
    Formulario necesario para realizar la carga de los nuevos documentos.
    '''
    NAME = 'documento_form'
    SUBMIT = 'documento_submit'

    class Meta:
        model = Documento
        fields = ('tipo_documento', 'file')
        widgets = {
            'tipo_documento': forms.HiddenInput()
        }

    def save(self, commit=True, tramite=None):
        doc = super(FormularioDocumento, self).save(commit=False)
        if tramite:
            doc.tramite = tramite
        if commit:
            doc.save()
        return doc


class FormularioDocumentosSetBase(BaseFormSet):
    '''
    Fomset de formularios tipo FormularioDocumentosSetBase.
    '''
    def __init__(self, *args, **kwargs):
        super(FormularioDocumentosSetBase, self).__init__(*args, **kwargs)
        self.helper = FormHelper()

        self.helper.form_tag = False


def FormularioDocumentoSetFactory(tipos):
    '''
    Funcion FormularioDocumentoSetFactory:
    Se encarga de crear una ristra de formularios de documento del tipo que reciba como parametro
    :param tipos: tipos de documento a crear
    :return: objeto Formset de documentos.
    '''
    return formset_factory(FormularioDocumento,
        formset=FormularioDocumentosSetBase,
        max_num=len(tipos), extra=len(tipos))


def metodo(tipos):
    '''
    Funcion metodo:
    Funcion que devuelve una lista de tipos de documento junto a su pk correspondiente.
    :param tipos: tipos de documento a utilizar
    :return initial: lista de tipos de documento
    '''
    initial = []
    for t in tipos:
        initial.append({'tipo_documento': t.pk})
    return initial
