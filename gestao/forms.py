from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User
from django.template.defaultfilters import filesizeformat

from dal import autocomplete

from ckeditor.widgets import CKEditorWidget

from adesao.models import Usuario
from adesao.models import Historico
from adesao.models import Cidade
from adesao.models import Uf
from adesao.models import Municipio
from adesao.models import SistemaCultura
from adesao.models import LISTA_ESTADOS_PROCESSO
from adesao.models import SistemaCultura


from planotrabalho.models import CriacaoSistema, FundoCultura, Componente
from planotrabalho.models import PlanoCultura, OrgaoGestor, ConselhoCultural
from planotrabalho.models import SituacoesArquivoPlano

from gestao.models import Diligencia, DiligenciaSimples

from .utils import enviar_email_alteracao_situacao

from adesao.utils import validar_cpf

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

max_upload_size = 5242880


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


class InserirSEI(ModelForm):
    processo_sei = forms.CharField(max_length="50", required=False)

    class Meta:
        model = Usuario
        fields = ('processo_sei',)


class CadastradorEnte(forms.ModelForm):
    cpf_cadastrador = forms.CharField(max_length="20")
    data_publicacao_acordo = forms.DateField(required=False)

    def clean_cpf_cadastrador(self):
        if not validar_cpf(self.cleaned_data['cpf_cadastrador']):
            raise forms.ValidationError('Por favor, digite um CPF válido!')

        try:
            Usuario.objects.get(user__username=self.cleaned_data['cpf_cadastrador'])
        except Usuario.DoesNotExist:
            raise forms.ValidationError('Este CPF não está cadastrado.')

        return self.cleaned_data['cpf_cadastrador']

    def save(self):
        sistema = self.instance
        cadastrador = Usuario.objects.get(user__username=self.cleaned_data['cpf_cadastrador'])
        sistema.cadastrador = cadastrador

        if self.cleaned_data['data_publicacao_acordo']:
            sistema.data_publicacao_acordo = self.cleaned_data['data_publicacao_acordo']

        sistema.save()

        return sistema

    class Meta:
        model = SistemaCultura
        fields = ["cpf_cadastrador", "data_publicacao_acordo"]


class AlterarDadosAdesao(ModelForm):
    processo_sei = forms.CharField(max_length="50", required=False)
    justificativa = forms.CharField(required=False)
    localizacao = forms.CharField(max_length="10", required=False)
    num_processo = forms.CharField(max_length="50", required=False)
    estado_processo = forms.ChoiceField(choices=LISTA_ESTADOS_PROCESSO, required=False)

    def clean(self):
        if self.cleaned_data.get('estado_processo', None) == '6':
            if not self.cleaned_data.get('data_publicacao_acordo', None):
                raise forms.ValidationError('Insira a data corretamente.')

    def save(self, commit=True):
        usuario = super(AlterarDadosAdesao, self).save(commit=False)
        historico = Historico()
        historico.usuario = usuario
        historico.situacao = self.cleaned_data['estado_processo']

        if self.cleaned_data['estado_processo'] == '2':
            usuario.municipio.localizacao = self.cleaned_data['localizacao']
        elif self.cleaned_data['estado_processo'] == '3':
            historico.descricao = self.cleaned_data['justificativa']
        elif self.cleaned_data['estado_processo'] == '4':
            usuario.municipio.numero_processo = self.cleaned_data['num_processo']

        if commit:
            usuario.municipio.save()
            usuario.save()
            historico.save()
            enviar_email_alteracao_situacao(usuario, historico)

    class Meta:
        model = Usuario
        fields = ('estado_processo', 'data_publicacao_acordo', 'link_publicacao_acordo',
                  'processo_sei')


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
    SITUACOES = (
        (0, "Em preenchimento"),
        (1, "Avaliando anexo"),
        (2, "Concluída"),
        (3, "Arquivo aprovado com ressalvas"),
        (4, "Arquivo danificado"),
        (5, "Arquivo incompleto"),
        (6, "Arquivo incorreto")
    )

    classificacao_arquivo = forms.TypedChoiceField(choices=SITUACOES, required=False)

    def __init__(self, *args, **kwargs):
        self.tipo_componente = kwargs.pop("componente")
        super(DiligenciaComponenteForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        diligencia = super(DiligenciaForm, self).save()

        if commit:
            componente = getattr(self.sistema_cultura, self.tipo_componente)
            componente.diligencia = diligencia
            componente.situacao = self.cleaned_data['classificacao_arquivo']
            componente.save()

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


class AlterarCadastradorForm(forms.Form):
    cpf_usuario = forms.CharField(max_length=11)
    data_publicacao_acordo = forms.DateField(required=False)

    def __init__(self, cod_ibge=None, *args, **kwargs):
        super(AlterarCadastradorForm, self).__init__(*args, **kwargs)
        self.cod_ibge = cod_ibge

    def clean_cpf_usuario(self):
        if not validar_cpf(self.cleaned_data['cpf_usuario']):
            raise forms.validationerror('por favor, digite um cpf válido!')

        try:
            user.objects.get(username=''.join(re.findall(
                '\d+',
                self.cleaned_data['cpf_usuario'])))
            return self.cleaned_data['cpf_usuario']
        except user.doesnotexist:
            raise forms.validationerror('esse cpf não está cadastrado.')

        return self.cleaned_data['cpf_usuario']

    def save(self):
        cadastrador_novo = usuario.objects.get(
                user__username=self.cleaned_data['cpf_usuario'])
        sistema = sistemacultura.sistema.get(ente_federado__cod_ibge=self.cod_ibge)
        sistema.data_publicacao_acordo = self.cleaned_data['data_publicacao_acordo']
        sistema.cadastrador = cadastrador_novo
        sistema.save()

        return sistema

    class Meta:
        fields = ('cpf_usuario', 'data_publicacao_acordo')


class AlterarUsuarioForm(ModelForm):
    is_active = forms.BooleanField(required=False)
    is_staff = forms.BooleanField(required=False)
    email = forms.EmailField(required=False)

    class Meta:
        model = User
        fields = ('is_active', 'is_staff', 'email')


class AlterarDocumentosEnteFederadoForm(ModelForm):
    termo_posse_prefeito = RestrictedFileField(
        content_types=content_types,
        max_upload_size=max_upload_size)
    rg_copia_prefeito = RestrictedFileField(
        content_types=content_types,
        max_upload_size=max_upload_size)
    cpf_copia_prefeito = RestrictedFileField(
        content_types=content_types,
        max_upload_size=max_upload_size)

    class Meta:
        model = Municipio
        fields = ('termo_posse_prefeito', 'rg_copia_prefeito', 'cpf_copia_prefeito')


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


class CriarComponenteForm(ModelForm):
    componentes = {
            "legislacao": 0,
            "orgao_gestor": 1,
            "fundo_cultura": 2,
            "conselho": 3,
            "plano": 4,
    }

    arquivo = RestrictedFileField(
        content_types=content_types,
        max_upload_size=max_upload_size)
    data_publicacao = forms.DateField(required=True)

    def __init__(self, *args, **kwargs):
        self.sistema = kwargs.pop('sistema')
        self.nome_componente = kwargs.pop('nome_componente')
        super(CriarComponenteForm, self).__init__(*args, **kwargs)

    def save(self, commit=True, *args, **kwargs):
        componente = super(CriarComponenteForm, self).save(commit=False)
        if 'arquivo' in self.changed_data:
            componente.situacao = 1

        if commit:
            componente.tipo = self.componentes.get(self.nome_componente)
            componente.arquivo = None
            componente.save()
            sistema_cultura = getattr(componente, self.nome_componente)
            sistema_cultura.add(self.sistema)
            componente.arquivo = self.cleaned_data['arquivo']
            componente.save()
            setattr(self.sistema, self.nome_componente, componente)
            self.sistema.save()

        return componente

    class Meta:
        model = Componente
        fields = ('arquivo', 'data_publicacao')
