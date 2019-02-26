import datetime
from django import forms
from django.forms import ModelForm
from django.forms.widgets import FileInput
from django.forms import inlineformset_factory

from localflavor.br.forms import BRCNPJField

from .models import CriacaoSistema, OrgaoGestor, ConselhoCultural
from .models import FundoCultura, Componente
from .models import FundoDeCultura, PlanoCultura
from .models import Conselheiro, SITUACAO_CONSELHEIRO
from planotrabalho.models import ArquivoComponente2
from planotrabalho.models import upload_to
from .utils import add_anos

SETORIAIS = (
    ('0', '-- Selecione um Segmento --'),
    ('1', 'Arquitetura e Urbanismo'),
    ('2', 'Arquivos'),
    ('3', 'Arte Digital'),
    ('4', 'Artes Visuais'),
    ('5', 'Artesanato'),
    ('6', 'Audiovisual'),
    ('7', 'Circo'),
    ('8', 'Culturas Afro-brasileiras'),
    ('9', 'Culturas dos Povos Indígenas'),
    ('10', 'Culturas Populares'),
    ('11', 'Dança'),
    ('12', 'Design'),
    ('13', 'Literatura, Livro e Leitura'),
    ('14', 'Moda'),
    ('15', 'Museus'),
    ('16', 'Música Erudita'),
    ('17', 'Música Popular'),
    ('18', 'Patrimônio Imaterial'),
    ('19', 'Patrimônio Material'),
    ('20', 'Teatro'),
    ('21', 'Outros')
    )


class CriarComponenteForm(ModelForm):
    componentes = {
            "legislacao": 0,
            "orgao_gestor": 1,
            "fundo_cultura": 2,
            "conselho": 3,
            "plano": 4,
    }

    arquivo = forms.FileField(required=True, widget=FileInput)
    data_publicacao = forms.DateField(required=True)

    def __init__(self, *args, **kwargs):
        self.sistema = kwargs.pop('sistema')
        self.tipo_componente = kwargs.pop('tipo')
        super(CriarComponenteForm, self).__init__(*args, **kwargs)

    def save(self, commit=True, *args, **kwargs):
        componente = super(CriarComponenteForm, self).save(commit=False)
        if 'arquivo' in self.changed_data:
            componente.situacao = 1

        if commit:
            componente.tipo = self.componentes.get(self.tipo_componente)
            componente.data_publicacao = self.cleaned_data['data_publicacao']
            componente.arquivo = None
            componente.save()
            sistema_cultura = getattr(componente, self.tipo_componente)
            sistema_cultura.add(self.sistema)
            componente.arquivo = self.cleaned_data['arquivo']
            componente.save()
            setattr(self.sistema, self.tipo_componente, componente)
            self.sistema.save()

        return componente

    class Meta:
        model = Componente
        fields = ('arquivo', 'data_publicacao')


class CriarFundoForm(CriarComponenteForm):
    cnpj = BRCNPJField()
    regulamentacao_arquivo = forms.FileField(required=False, widget=FileInput)

    def save(self, commit=True, *args, **kwargs):
        fundo = super(CriarFundoForm, self).save(commit=False)
        arquivo = self.cleaned_data['regulamentacao_arquivo']

        if not fundo.regulamentacao:
            fundo.tipo = 2
            fundo.arquivo = None
            fundo.save()
            if 'arquivo' in self.changed_data:
                fundo.situacao = 1
            fundo.arquivo = self.cleaned_data['arquivo']

            sistema_cultura = fundo.fundo_cultura
            sistema_cultura.add(self.sistema)

            fundo.regulamentacao = ArquivoComponente2()
            if 'regulamentacao_arquivo' in self.changed_data:
                fundo.regulamentacao.situacao = 1
            fundo.regulamentacao.save()

            fundo.regulamentacao.fundos.add(fundo)
            fundo.regulamentacao.arquivo = arquivo
            fundo.regulamentacao.save()

            self.sistema.fundo_cultura = fundo
            self.sistema.save()
        else:
            fundo.regulamentacao.arquivo = arquivo
            fundo.regulamentacao.save()
        
        fundo.save()

    class Meta:
        model = FundoDeCultura
        fields = ('cnpj', 'arquivo', 'data_publicacao',)


class CriarConselheiroForm(ModelForm):
    segmento = forms.ChoiceField(choices=SETORIAIS)
    outros = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        self.conselho_id = kwargs.pop('conselho')
        super(CriarConselheiroForm, self).__init__(*args, **kwargs)

    def clean_segmento(self):
        if self.cleaned_data['segmento'] == '0':
            raise forms.ValidationError("Este campo é obrigatório.")

        return self.cleaned_data['segmento']

    def clean(self):
        if self.cleaned_data['segmento'] == '21' and self.cleaned_data['outros'] == '':
            self.add_error('segmento', 'Este campo é obrigatório.')

    def save(self, commit=True, *args, **kwargs):
        conselheiro = super(CriarConselheiroForm, self).save(commit=False)
        conselho = Componente.objects.get(id=self.conselho_id)
        conselheiro.conselho = conselho
        conselheiro.data_cadastro = datetime.datetime.now()
        conselheiro.data_situacao = datetime.datetime.now()
        conselheiro.situacao = 1  # Situação 1 = Habilitado

        if self.cleaned_data['segmento'] == '21':  # outros
            outros = self.cleaned_data['outros']  # texto livre
            conselheiro.segmento = outros if outros else 'Outros'
        else:
            segmento = self.cleaned_data['segmento']
            conselheiro.segmento = dict(SETORIAIS).get(segmento)

        if commit:
            conselheiro.save()
        return conselheiro

    class Meta:
        model = Conselheiro
        exclude = ['conselho']


class AlterarConselheiroForm(ModelForm):
    segmento = forms.ChoiceField(choices=SETORIAIS)
    outros = forms.CharField(required=False)
    situacao = forms.ChoiceField(choices=SITUACAO_CONSELHEIRO, required=True)

    def __init__(self, *args, **kwargs):
        super(AlterarConselheiroForm, self).__init__(*args, **kwargs)
        self.fields['situacao'].required = False

    def clean_segmento(self):
        if self.cleaned_data['segmento'] == '0':
            raise forms.ValidationError("Este campo é obrigatório.")

        return self.cleaned_data['segmento']

    def clean(self):
        if self.cleaned_data['segmento'] == '21' and self.cleaned_data['outros'] == '':
            self.add_error('segmento', 'Este campo é obrigatório.')

    def save(self, commit=True, *args, **kwargs):
        conselheiro = super(AlterarConselheiroForm, self).save(commit=False)

        if self.cleaned_data['segmento'] == '21':  # outros
            outros = self.cleaned_data['outros']  # texto livre
            conselheiro.segmento = outros if outros else 'Outros'
        else:
            segmento = self.cleaned_data['segmento']
            conselheiro.segmento = dict(SETORIAIS).get(segmento)

        if commit:
            conselheiro.save()
        return conselheiro

    class Meta:
        model = Conselheiro
        exclude = ['conselho', 'situacao']


class DesabilitarConselheiroForm(ModelForm):

    def save(self, commit=True, *args, **kwargs):
        conselheiro = super(DesabilitarConselheiroForm, self).save(commit=False)

        conselheiro.data_situacao = datetime.datetime.now()
        conselheiro.situacao = 0  # Situação 0 = Desabilitado

        if commit:
            conselheiro.save()
        return conselheiro

    class Meta:
        model = Conselheiro
        fields = ['situacao', 'data_situacao']
