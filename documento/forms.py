from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout
from .models import *
from django.forms import BaseFormSet
from django.forms import formset_factory
from documento.models import *

class FormularioDocumento(forms.ModelForm):
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
        doc.tramite=tramite
        if commit:
            doc.save()
        return doc

class FormularioDocumentosSetBase(BaseFormSet):
    def __init__(self, *args, **kwargs):
        super(FormularioDocumentosSetBase, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False

def FormularioDocumentoSetFactory(tipos):
    return formset_factory(FormularioDocumento,
        formset=FormularioDocumentosSetBase,
        max_num=len(tipos), extra=len(tipos))

def metodo(tipos):
    initial = []
    for t in tipos:
        initial.append({'tipo_documento': t.pk})
    return initial