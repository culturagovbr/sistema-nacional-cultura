from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.utils.crypto import get_random_string
from django.forms import ModelForm
from django.template.defaultfilters import filesizeformat
from django.forms import formset_factory

from dal import autocomplete
from localflavor.br.forms import BRCNPJField, BRCPFField

from snc.forms import RestrictedFileField

from .models import Usuario, Municipio, Responsavel
from .models import Secretario, Funcionario, SistemaCultura, Sede, Gestor
from .utils import limpar_mascara
import re

content_types = [
    'image/png',
    'image/jpg',
    'image/jpeg',
    'application/pdf',
    'application/msword',
    'application/vnd.oasis.opendocument.text',
    'application/vnd.openxmlformats-officedocument.' +
    'wordprocessingml.document',
    'application/x-rar-compressed',
    'application/zip',
    'application/octet-stream',
    'text/plain']


class CadastrarUsuarioForm(UserCreationForm):
    username = BRCPFField()
    confirmar_email = forms.EmailField(required=True)
    email = forms.EmailField(required=True)
    nome_usuario = forms.CharField(max_length=100)

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')

    def clean_confirmar_email(self):
        if self.data.get('email') != self.cleaned_data['confirmar_email']:
            raise forms.ValidationError(
                'Confirmação de e-mail não confere.')

        return self.cleaned_data['confirmar_email']

    def clean_email(self):
        try:
            User.objects.get(email=self.cleaned_data['email'])
            raise forms.ValidationError('Este e-mail já foi cadastrado!')
        except User.DoesNotExist:
            return self.cleaned_data['email']

    def clean_username(self):
        try:
            User.objects.get(username=''.join(re.findall(
                '\d+',
                self.cleaned_data['username'])))
            raise forms.ValidationError('Esse CPF já foi cadastrado.')
        except User.DoesNotExist:
            return self.cleaned_data['username']

        return self.cleaned_data['username']

    def save(self, commit=True):
        user = super(CadastrarUsuarioForm, self).save(commit=False)
        user.username = limpar_mascara(self.cleaned_data['username'])
        user.email = self.cleaned_data['email']
        user.is_active = False
        if commit:
            user.save()

        usuario = Usuario()
        usuario.user = user
        usuario.nome_usuario = self.cleaned_data['nome_usuario']
        codigo_ativacao = get_random_string()
        usuario.codigo_ativacao = codigo_ativacao
        if commit:
            usuario.save()

        return user


class CadastrarGestor(ModelForm):
    cpf = BRCPFField()
    termo_posse = RestrictedFileField(
        content_types=content_types,
        max_upload_size=52428800)
    rg_copia = RestrictedFileField(
        content_types=content_types,
        max_upload_size=52428800)
    cpf_copia = RestrictedFileField(
        content_types=content_types,
        max_upload_size=52428800)

    class Meta:
        model = Gestor
        exclude = ('tipo_funcionario',)


class CadastrarSede(ModelForm):
    cnpj = BRCNPJField()

    class Meta:
        model = Sede
        fields = '__all__'


class CadastrarSistemaCulturaForm(ModelForm):

    def clean(self):    
        super(CadastrarSistemaCulturaForm, self).clean()

        if 'ente_federado' in self.changed_data:
            sistema_cultura = SistemaCultura.sistema.filter(
                ente_federado=self.cleaned_data['ente_federado'])

            if sistema_cultura:
                self.add_error(
                    'ente_federado', 'Este ente federado já foi cadastrado!')

    class Meta:
        model = SistemaCultura
        fields = ('ente_federado', 'conferencia_nacional')
        widgets = {
            'ente_federado': autocomplete.ModelSelect2(url='gestao:ente_chain')}


class CadastrarFuncionarioForm(ModelForm):
    cpf = BRCPFField()

    class Meta:
        model = Funcionario
        exclude = ('tipo_funcionario',)
