from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout
from .models import *
from django.forms import BaseFormSet
from django.forms import formset_factory

class FormularioDocumento(forms.ModelForm):
    NAME = 'documento_form'
    SUBMIT = 'documento_submit'

    class Meta:
        model = Documento
        fields = ('tipo_documento', 'file')
        widgets = {
            'tipo_documento': forms.HiddenInput()
        }


class FormularioDocumentosSetBase(BaseFormSet):
    def __init__(self, *args, **kwargs):
        super(FormularioDocumentosSetBase, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False


def FormularioDocumentoSetFactory(tipos):
    return formset_factory(FormularioDocumento,
        formset=FormularioDocumentosSetBase,
        max_num=len(tipos), extra=len(tipos))
    '''initial = []
    for t in tipos:
        initial.append({'tipo_documento': t.pk})
    if request.method == "POST":
        return klass(request.POST, initial=initial)
    return klass(initial=initial)'''

