from django import forms
from django.template.defaultfilters import filesizeformat
from localflavor.br.forms import BRCNPJField
from snc.client import Client
from django.contrib.auth.forms import PasswordResetForm


class RestrictedFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        self.content_types = kwargs.pop("content_types")
        self.max_upload_size = kwargs.pop("max_upload_size")

        super(RestrictedFileField, self).__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        file = super(RestrictedFileField, self).clean(data, initial)

        try:
            content_type = file.content_type
            if content_type in self.content_types:
                if file._size > self.max_upload_size:
                    raise forms.ValidationError(
                        'O arquivo deve ter menos de %s. Tamanho atual %s'
                        % (filesizeformat(self.max_upload_size),
                           filesizeformat(file._size)))
            else:
                raise forms.ValidationError(
                    'Arquivos desse tipo não são aceitos.')
        except AttributeError:
            pass

        return data


class BRCNPJField(BRCNPJField):

    def clean(self, data):
        cnpj = super(BRCNPJField, self).clean(data)

        if data:
            consulta = Client().consulta_cnpj(cnpj)

            if not consulta:
                raise forms.ValidationError('CNPJ Inválido')

        return data

class CPFPasswordResetForm(PasswordResetForm):
    CPF = forms.CharField(widget=forms.TextInput(attrs={'data-mask':"000.000.000-00"}))
    email = forms.CharField(required=False)

    def clean_CPF(self):
        dirty_cpf = self.data.get('CPF')
        semi_dirty_cpf = dirty_cpf.translate({ord('.'): None})
        cpf = semi_dirty_cpf.translate({ord('-'): None})
        self.cleaned_data['CPF'] = cpf
        return self.cleaned_data['CPF']
    