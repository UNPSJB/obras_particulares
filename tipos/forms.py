from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from .models import *

class FormularioTipoDocumento(forms.ModelForm):
    NAME = 'tipo_documento_form'
    SUBMIT = 'tipo_documento_submit'
    class Meta:
        model = TipoDocumento
        fields = ('nombre', 'descripcion', 'activo', 'fecha_alta', 'requerido')

    #Esto es para el crispy
    def __init__(self, *args, **kwargs):
        super(FormularioTipoDocumento, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        #self.helper.form_class = 'form-horizontal'
        self.helper.add_input(Submit(self.SUBMIT, 'Guardar'))
        self.fields['requerido'] = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,
                                                             choices=TipoDocumento.ACCIONES)

    def clean_requerido(self):
        flags = [int(e) for e in self.cleaned_data['requerido']]

        # aca llamo al metodo y le puse print para ver si me traia la lista
        # con los tipos y si.. funciona! asiq podes llamar a este metodo desde
        # otra clase donde lo quieras usar. aca justamente no va pero lo estaba haciendo
        # en modo debbuging jaja

        print(TipoDocumento.get_tipos_documentos_para_momento("INICIAR"))

        # asiq podes borrarlo o dejarlo, no importa. el metodo esta definido en
        # el modelo de tipo. asiq ahi podes verlo. lo vemo!


        return sum(flags)

class FormularioTipoObra(forms.ModelForm):
    NAME = 'tipo_obra_form'
    SUBMIT = 'tipo_obra_submit'
    class Meta:
        model = TipoObra
        fields = ('nombre','descripcion','categorias')

    def __init__(self, *args, **kwargs):
        super(FormularioTipoObra, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        #self.helper.form_class = 'form-horizontal'
        self.helper.add_input(Submit('tipo_obra_submit', 'Guardar'))
