from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User
from django.template.defaultfilters import filesizeformat

from localflavor.br.forms import BRCPFField

from dal import autocomplete

from ckeditor.widgets import CKEditorWidget

from snc.forms import RestrictedFileField

from adesao.models import Usuario
from adesao.models import Historico
from adesao.models import Cidade
from adesao.models import Uf
from adesao.models import Municipio
from adesao.models import LISTA_ESTADOS_PROCESSO
from adesao.models import SistemaCultura, Gestor


from planotrabalho.models import CriacaoSistema, FundoCultura, Componente
from planotrabalho.models import PlanoCultura, OrgaoGestor, ConselhoCultural
from planotrabalho.models import SituacoesArquivoPlano

from gestao.models import Diligencia, DiligenciaSimples, LISTA_SITUACAO_ARQUIVO

from .utils import enviar_email_alteracao_situacao

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

max_upload_size = 52428800

class InserirSEI(ModelForm):
    processo_sei = forms.CharField(max_length="50", required=False)

    class Meta:
        model = Usuario
        fields = ('processo_sei',)


class CadastradorEnte(forms.ModelForm):
    cpf_cadastrador = BRCPFField()

    def clean_cpf_cadastrador(self):
        try:
            Usuario.objects.get(user__username=self.cleaned_data['cpf_cadastrador'])
        except Usuario.DoesNotExist:
            raise forms.ValidationError('Este CPF não está cadastrado.')

        return self.cleaned_data['cpf_cadastrador']

    def save(self):
        sistema = self.instance
        cadastrador = Usuario.objects.get(user__username=self.cleaned_data['cpf_cadastrador'])
        sistema.cadastrador = cadastrador
        sistema.save()

        return sistema

    class Meta:
        model = SistemaCultura
        fields = ["cpf_cadastrador"]


class AlterarDadosEnte(ModelForm):
    justificativa = forms.CharField(required=False)
    localizacao = forms.CharField(max_length="10", required=False)
    estado_processo = forms.ChoiceField(choices=LISTA_ESTADOS_PROCESSO, required=False)

    def clean_estado_processo(self):
        if self.cleaned_data.get('estado_processo', None) != '6':
            if self.instance.data_publicacao_acordo:
                self.instance.data_publicacao_acordo = None

        return self.cleaned_data['estado_processo']

    class Meta:
        model = SistemaCultura
        fields = ('processo_sei', 'justificativa', 'localizacao',
                  'estado_processo', 'data_publicacao_acordo','data_publicacao_reatificacao',
                  'link_publicacao_acordo', 'link_publicacao_reatificacao')


class DiligenciaForm(ModelForm):

    texto_diligencia = forms.CharField(widget=CKEditorWidget(), required=False)

    def __init__(self, *args, **kwargs):
        self.sistema_cultura = kwargs.pop("sistema_cultura")
        usuario = kwargs.pop("usuario")
        super(DiligenciaForm, self).__init__(*args, **kwargs)
        self.instance.usuario = usuario

    def clean_texto_diligencia(self):
        CONCLUIDA = '2'
        if self.data.get('classificacao_arquivo', False) != CONCLUIDA:
            if not self.data.get('texto_diligencia', False):
                raise forms.ValidationError('Por favor, adicione o texto da diligência!')

        return self.cleaned_data['texto_diligencia']

    class Meta:
        model = DiligenciaSimples
        fields = ('texto_diligencia',)


class DiligenciaComponenteForm(DiligenciaForm):
    classificacao_arquivo = forms.TypedChoiceField(
        choices=LISTA_SITUACAO_ARQUIVO, required=False)

    def __init__(self, *args, **kwargs):
        self.tipo_componente = kwargs.pop("componente")
        self.arquivo = kwargs.pop("arquivo")
        super(DiligenciaComponenteForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        diligencia = super(DiligenciaForm, self).save()

        if commit:
            componente = getattr(self.sistema_cultura, self.tipo_componente)
            if self.arquivo == 'arquivo':     
                componente.diligencia = diligencia
                componente.situacao = self.cleaned_data['classificacao_arquivo']
                componente.save()
            else:
                arquivo = getattr(componente, self.arquivo)
                arquivo.diligencia = diligencia
                arquivo.situacao = self.cleaned_data['classificacao_arquivo']
                arquivo.save()

    class Meta:
        model = DiligenciaSimples
        fields = ('texto_diligencia', 'classificacao_arquivo')


class DiligenciaGeralForm(DiligenciaForm):

    def __init__(self, *args, **kwargs):
        super(DiligenciaGeralForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        diligencia = super(DiligenciaForm, self).save()

        if commit:
            self.sistema_cultura.diligencia = diligencia
            self.sistema_cultura.save()


class AlterarUsuarioForm(ModelForm):
    is_active = forms.BooleanField(required=False)
    is_staff = forms.BooleanField(required=False)
    email = forms.EmailField(required=False)

    class Meta:
        model = User
        fields = ('is_active', 'is_staff', 'email')


class AlterarDocumentosEnteFederadoForm(ModelForm):
    termo_posse = RestrictedFileField(
        content_types=content_types,
        max_upload_size=max_upload_size)
    rg_copia = RestrictedFileField(
        content_types=content_types,
        max_upload_size=max_upload_size)
    cpf_copia = RestrictedFileField(
        content_types=content_types,
        max_upload_size=max_upload_size)

    class Meta:
        model = Gestor
        fields = ('termo_posse', 'rg_copia', 'cpf_copia')


class AlterarComponenteForm(ModelForm):
    arquivo = RestrictedFileField(
        content_types=content_types,
        max_upload_size=max_upload_size)
    data_publicacao = forms.DateField(required=True)

    def save(self, commit=True, *args, **kwargs):
        sistema = super(AlterarComponenteForm, self).save(commit=False)
        if 'arquivo' in self.changed_data:
            sistema.situacao = 1

        if commit:
            sistema.save()

        return sistema

    class Meta:
        model = Componente
        fields = ('arquivo', 'data_publicacao')
