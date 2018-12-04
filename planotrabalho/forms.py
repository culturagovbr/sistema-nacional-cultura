import datetime
from django import forms
from django.forms import ModelForm
from django.forms.widgets import FileInput

from .models import CriacaoSistema, OrgaoGestor, ConselhoCultural, FundoCultura, Componente
from .models import FundoCultura, FundoDeCultura, PlanoCultura, Conselheiro, SITUACAO_CONSELHEIRO
from .utils import validar_cnpj, add_anos

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

    class Meta:
        model = FundoDeCultura
        fields = ('cnpj', 'arquivo', 'data_publicacao')


class ConselhoCulturalForm(ModelForm):
    arquivo = forms.FileField(required=True, widget=FileInput)
    data_publicacao = forms.DateField(required=True)

    def __init__(self, *args, **kwargs):
        self.usuario = kwargs.pop('user')
        super(ConselhoCulturalForm, self).__init__(*args, **kwargs)

    def clean(self):
        limite = add_anos(self.usuario.data_publicacao_acordo, self.usuario.prazo)
        hoje = datetime.date.today()
        if hoje > limite:
            self.add_error('arquivo', '''Não foi possível salvar.
                Você ultrapassou a data limite de envio: ''' + limite.strftime("%d/%m/%Y"))

    def save(self, commit=True, *args, **kwargs):
        conselho = super(ConselhoCulturalForm, self).save(commit=False)
        if 'arquivo' in self.changed_data:
            conselho.situacao_id = 1

        if commit:
            conselho.planotrabalho = self.usuario.plano_trabalho
            conselho.save()
            self.usuario.plano_trabalho.conselho_cultural = conselho
            self.usuario.plano_trabalho.save()

            nomes = self.data.getlist('conselheiro')
            emails = self.data.getlist('email')
            segmentos = self.data.getlist('segmento')
            outros_segmentos = self.data.getlist('outros_segmento')
            for nome, email, segmento, outros_segmento in zip(nomes, emails, segmentos, outros_segmentos):
                if nome and email and segmento:
                    try:
                        conselheiro = Conselheiro.objects.get(email=email, conselho=conselho)
                        conselheiro.nome, conselheiro.email, conselheiro.conselho = nome, email, conselho
                        conselheiro.segmento = segmento if segmento != 'Outros' else outros_segmento
                        conselheiro.save()
                    except Conselheiro.DoesNotExist:
                        Conselheiro.objects.get_or_create(nome=nome, email=email, segmento=segmento, conselho=conselho)
                else:
                    Conselheiro.objects.filter(nome=nome, email=email, conselho=conselho).delete()
            Conselheiro.objects.filter(conselho=conselho).exclude(email__in=emails).delete()
        return conselho

    class Meta:
        model = ConselhoCultural
        fields = ['arquivo', 'data_publicacao']


class CriarConselheiroForm(ModelForm):
    segmento = forms.ChoiceField(choices=SETORIAIS)
    outros = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        self.usuario = kwargs.pop('user')
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
        conselheiro.conselho = self.usuario.plano_trabalho.conselho_cultural
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
        self.usuario = kwargs.pop('user')
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
        conselheiro.conselho = self.usuario.plano_trabalho.conselho_cultural

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

    def __init__(self, *args, **kwargs):
        self.usuario = kwargs.pop('user')
        super(DesabilitarConselheiroForm, self).__init__(*args, **kwargs)

    def save(self, commit=True, *args, **kwargs):
        conselheiro = super(DesabilitarConselheiroForm, self).save(commit=False)
        conselheiro.conselho = self.usuario.plano_trabalho.conselho_cultural

        conselheiro.data_situacao = datetime.datetime.now()
        conselheiro.situacao = 0  # Situação 0 = Desabilitado

        if commit:
            conselheiro.save()
        return conselheiro

    class Meta:
        model = Conselheiro
        fields = ['situacao', 'data_situacao']
