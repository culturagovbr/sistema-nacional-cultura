from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User

from localflavor.br.forms import BRCPFField

from ckeditor.widgets import CKEditorWidget

from snc.forms import RestrictedFileField
from snc.widgets import FileUploadWidget

from adesao.models import Usuario
from adesao.models import LISTA_ESTADOS_PROCESSO
from adesao.models import SistemaCultura, Gestor, Usuario


from planotrabalho.models import CriacaoSistema, FundoCultura, Componente
from planotrabalho.models import PlanoCultura, OrgaoGestor, ConselhoCultural
from planotrabalho.models import SituacoesArquivoPlano
from planotrabalho.models import LISTA_TIPOS_COMPONENTES

from gestao.models import Diligencia, DiligenciaSimples, LISTA_SITUACAO_ARQUIVO
from gestao.models import Contato

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
    oficio_cadastrador = RestrictedFileField(
        widget=FileUploadWidget(),
        content_types=content_types,
        max_upload_size=max_upload_size)

    def __init__(self, *args, **kwargs):
        super(CadastradorEnte, self).__init__(*args, **kwargs)
        self.fields['oficio_cadastrador'].widget.attrs = {
            'label': 'Ofício de Indicação do Cadastrador'}

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
        fields = ["cpf_cadastrador", "oficio_cadastrador"]


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
                  'estado_processo', 'data_publicacao_acordo','data_publicacao_retificacao',
                  'link_publicacao_acordo', 'link_publicacao_retificacao')


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
        choices=LISTA_SITUACAO_ARQUIVO[1:7], required=False)

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
                componente.save(update_fields={"diligencia", "situacao"})
            else:
                arquivo = getattr(componente, self.arquivo)
                arquivo.diligencia = diligencia
                arquivo.situacao = self.cleaned_data['classificacao_arquivo']
                arquivo.save(update_fields={"diligencia", "situacao"})

            if self.tipo_componente == "legislacao":
                if self.sistema_cultura.fundo_cultura and self.sistema_cultura.fundo_cultura.arquivo == componente.arquivo:
                    self.sistema_cultura.fundo_cultura.diligencia = diligencia
                    self.sistema_cultura.fundo_cultura.situacao = self.cleaned_data['classificacao_arquivo']
                    self.sistema_cultura.fundo_cultura.save()

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
        widget=FileUploadWidget(),
        content_types=content_types,
        max_upload_size=max_upload_size)
    data_publicacao = forms.DateField(required=True)

    def __init__(self, *args, **kwargs):
        super(AlterarComponenteForm, self).__init__(*args, **kwargs)
        pk = str(kwargs.get('instance', None))
        componente = Componente.objects.get(pk=pk)

        self.fields['arquivo'].widget.attrs = {'label': componente.nome_componente}

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


class CriarContatoForm(ModelForm):

    def __init__(self, sistema, *args, **kwargs):
        super(CriarContatoForm, self).__init__(*args, **kwargs)
        self.sistema = sistema

    def save(self, commit=True, *args, **kwargs):
        contato = super(CriarContatoForm, self).save(commit=False)
        contato.sistema_cultura = self.sistema
        contato.save()

        return contato

    class Meta:
        model = Contato
        fields = ('contatado', 'data', 'discussao',)


class AditivarPrazoForm(ModelForm):
    oficio_prorrogacao_prazo = RestrictedFileField(
        widget=FileUploadWidget(),
        content_types=content_types,
        max_upload_size=max_upload_size)

    def __init__(self, *args, **kwargs):
        super(AditivarPrazoForm, self).__init__(*args, **kwargs)
        self.fields['oficio_prorrogacao_prazo'].widget.attrs = {
            'label': 'Ofício de Prorrogação do Prazo'}

    class Meta:
        model = SistemaCultura
        fields = ('oficio_prorrogacao_prazo',)

class GerarListaDeEmailsForm(forms.Form):
    UFS = [
        (0, "Todos"),
        (12, "AC"),
        (27, "AL"),
        (13, "AM"),
        (16, "AP"),
        (29, "BA"),
        (23, "CE"),
        (53, "DF"),
        (32, "ES"),
        (52, "GO"),
        (21, "MA"),
        (31, "MG"),
        (50, "MS"),
        (51, "MT"),
        (15, "PA"),
        (25, "PB"),
        (26, "PE"),
        (22, "PI"),
        (41, "PR"),
        (33, "RJ"),
        (24, "RN"),
        (11, "RO"),
        (14, "RR"),
        (43, "RS"),
        (42, "SC"),
        (28, "SE"),
        (35, "SP"),
        (17, "TO")
    ]
    uf = forms.CharField(label='UF', widget=forms.Select(choices=UFS))
    estados = forms.BooleanField(required=False)
    municipios = forms.BooleanField(required=False)
    aguardando_preenchimento_dos_dados_cadastrais = forms.BooleanField(required=False)
    aguardando_envio_da_documentacao = forms.BooleanField(required=False)
    aguardando_renovacao_da_adesao = forms.BooleanField(required=False)
    diligencia_documental = forms.BooleanField(required=False)
    aguardando_analise_do_plano_de_trabalho = forms.BooleanField(required=False)
    publicado_no_dou = forms.BooleanField(required=False)
    acordo_de_cooperação_e_termo_de_adesao_aprovados = forms.BooleanField(required=False)
    
    