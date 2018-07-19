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


from planotrabalho.models import CriacaoSistema, FundoCultura
from planotrabalho.models import PlanoCultura, OrgaoGestor, ConselhoCultural
from planotrabalho.models import SituacoesArquivoPlano

from gestao.models import Diligencia

from .utils import enviar_email_alteracao_situacao


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
    texto_diligencia = forms.CharField(widget=CKEditorWidget())

    def __init__(self, resultado, componente, *args, **kwargs):
        """ Form da diligência recebe como parâmetro o resultado, que serve
        para diferenciar diligência de aprovação e reprovação """

        super(DiligenciaForm, self).__init__(*args, **kwargs)

        if componente != 'plano_trabalho':
            if resultado == '1':
                self.fields['classificacao_arquivo'].queryset = SituacoesArquivoPlano.objects.filter(pk=2)
            else:
                self.fields['classificacao_arquivo'].queryset = SituacoesArquivoPlano.objects.filter(id__gte=4, id__lte=6)
        else:
            self.fields.pop('classificacao_arquivo')

    class Meta:
        model = Diligencia
        fields = ('texto_diligencia', 'classificacao_arquivo')


class AlterarCadastradorForm(forms.Form):
    cpf_usuario = forms.CharField(max_length=11)
    estado = forms.ModelChoiceField(queryset=Uf.objects.all(),
                                    widget=autocomplete.ModelSelect2(url='gestao:uf_chain'))
    municipio = forms.ModelChoiceField(
        queryset=Cidade.objects.all(),
        widget=autocomplete.ModelSelect2(url='gestao:cidade_chain',
                                         forward=['estado'])
        )
    data_publicacao_acordo = forms.DateField(required=False)

    def save(self):
        cadastrador_novo = Usuario.objects.get(
                user__username=self.cleaned_data['cpf_usuario'])
        sistema = SistemaCultura.objects.ativo_ou_cria(
                cidade=self.cleaned_data.get('municipio', None),
                uf=self.cleaned_data['estado'])

        sistema.cadastrador = cadastrador_novo
        sistema.save()

        return sistema

    class Meta:
        fields = ('cpf_usuario', 'estado', 'municipio', 'data_publicacao_acordo')


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


class AlterarSistemaForm(ModelForm):
    arquivo = RestrictedFileField(
        content_types=content_types,
        max_upload_size=max_upload_size)

    class Meta:
        model = CriacaoSistema
        fields = ('arquivo',)


class AlterarFundoForm(ModelForm):
    arquivo = RestrictedFileField(
        content_types=content_types,
        max_upload_size=max_upload_size)

    class Meta:
        model = FundoCultura
        fields = ('arquivo',)


class AlterarPlanoForm(ModelForm):
    arquivo = RestrictedFileField(
        content_types=content_types,
        max_upload_size=max_upload_size)

    class Meta:
        model = PlanoCultura
        fields = ('arquivo',)


class AlterarOrgaoForm(ModelForm):
    arquivo = RestrictedFileField(
        content_types=content_types,
        max_upload_size=max_upload_size)

    class Meta:
        model = OrgaoGestor
        fields = ('arquivo',)


class AlterarConselhoForm(ModelForm):
    arquivo = RestrictedFileField(
        content_types=content_types,
        max_upload_size=max_upload_size)

    class Meta:
        model = ConselhoCultural
        fields = ('arquivo',)
