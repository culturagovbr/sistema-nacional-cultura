from rest_framework import serializers
from drf_hal_json.fields import HalHyperlinkedIdentityField
from drf_hal_json import serializers as hal_serializers

from adesao.models import Municipio
from adesao.models import Uf
from adesao.models import Cidade
from planotrabalho.models import Componente
from planotrabalho.models import Conselheiro
from planotrabalho.models import FundoDeCultura
from planotrabalho.models import PlanoDeCultura


from adesao.models import SistemaCultura
from adesao.models import EnteFederado
from adesao.models import Sede
from adesao.models import Gestor


class ComponenteSCSerializer(hal_serializers.HalModelSerializer):
    situacao = serializers.CharField(source='get_situacao_display')
    cod_situacao = serializers.CharField(source='situacao')

    class Meta:
        model = Componente
        fields = ('cod_situacao', 'situacao', 'data_envio', 'data_publicacao', 'arquivo')


class ConselheirosSerializer(hal_serializers.HalModelSerializer):
    situacao = serializers.SerializerMethodField(source='situacao')
    cod_situacao = serializers.CharField(source='situacao')

    class Meta:
        model = Conselheiro
        fields = (
            'nome',
            'email',
            'segmento',
            'cod_situacao',
            'situacao',
            'data_cadastro',
            'data_situacao'
        )

    def get_situacao(self, obj):
        return obj.get_situacao_display()


class ConselhoComponenteSerializer(hal_serializers.HalModelSerializer):
    conselho = serializers.SerializerMethodField(source='conselho')

    class Meta:
        model = Componente
        fields = ('conselho', )

    def get_conselho(self, obj):

        context = {}
        context['request'] = self.context['request']
        serializer = ConselheirosSerializer(
            many=True,
            read_only=True,
            instance=Conselheiro.objects.filter(
                conselho_id=obj.id),
            context=context)

        return serializer.data

    def to_representation(self, instance):
        context = super(ConselhoComponenteSerializer, self).\
            to_representation(instance)

        conselheiros = context['conselho']['_embedded']['items']
        return {
            'conselheiros': conselheiros
        }


class FundoComponenteSerializer(hal_serializers.HalModelSerializer):
    situacao = serializers.CharField(source='get_situacao_display')
    cod_situacao = serializers.CharField(source='situacao')

    class Meta:
        model = FundoDeCultura
        fields = ('cod_situacao', 'situacao', 'data_envio', 'arquivo', 'cnpj')


class PlanoTrabalhoSCSerializer(hal_serializers.HalModelSerializer):
    criacao_lei_sistema = ComponenteSCSerializer(source='legislacao')
    criacao_orgao_gestor = ComponenteSCSerializer(source='orgao_gestor')
    criacao_plano_cultura = ComponenteSCSerializer(source='plano')
    criacao_plano_metas = serializers.SerializerMethodField()
    criacao_conselho_cultural_ata = ComponenteSCSerializer(source='conselho')
    criacao_conselho_cultural_lei = serializers.SerializerMethodField()
    criacao_fundo_cultura = FundoComponenteSerializer(source='fundo_cultura')
    criacao_fundo_cultura_cnpj = serializers.SerializerMethodField()
    self = HalHyperlinkedIdentityField(view_name='api:planotrabalho-detail')

    def get_criacao_conselho_cultural_lei(self, obj):
        if getattr(obj.conselho, 'lei', None):
            return ComponenteSCSerializer(
                instance=obj.conselho.lei,
                context=self.context
            ).data
            context = super(PlanoTrabalhoSCSerializer, self).to_representation(instance)
            context['_embedded']['criacao_conselho_cultural_lei'] = context['criacao_conselho_cultural_lei']
            del context['criacao_conselho_cultural_lei']
        return None

    def get_criacao_fundo_cultura_cnpj(self, obj):
        if getattr(obj.fundo_cultura, 'comprovante_cnpj', None):
            return ComponenteSCSerializer(
                instance=obj.fundo_cultura.comprovante_cnpj,
                context=self.context
            ).data
        return None

    def get_criacao_plano_metas(self, obj):
        if getattr(obj.plano, 'metas', None):
            return ComponenteSCSerializer(
                instance=obj.plano.metas,
                context=self.context
            ).data
        return None

    def to_representation(self, instance):
        context = super(PlanoTrabalhoSCSerializer, self).to_representation(instance)
        context['_embedded']['criacao_conselho_cultural_lei'] = context['criacao_conselho_cultural_lei']
        del context['criacao_conselho_cultural_lei']
        context['_embedded']['criacao_fundo_cultura_cnpj'] = context['criacao_fundo_cultura_cnpj']
        del context['criacao_fundo_cultura_cnpj']
        context['_embedded']['criacao_plano_metas'] = context['criacao_plano_metas']
        del context['criacao_plano_metas']
        return context

    class Meta:
        model = SistemaCultura
        fields = (
            'id',
            'self',
            'criacao_lei_sistema',
            'criacao_orgao_gestor',
            'criacao_plano_cultura',
            'criacao_plano_metas',
            'criacao_fundo_cultura',
            'criacao_fundo_cultura_cnpj',
            'criacao_conselho_cultural_lei',
            'criacao_conselho_cultural_ata')


class PlanoTrabalhoSerializer(PlanoTrabalhoSCSerializer):

    class Meta:
        model = SistemaCultura
        fields = (
            'id',
            'self',
            'criacao_lei_sistema',
            'criacao_conselho_cultural_ata',
            'criacao_conselho_cultural_lei')


class SedeSerializer(hal_serializers.HalModelSerializer):
    telefones = serializers.SerializerMethodField(source='telefones')
    localizacao = serializers.SerializerMethodField(source='localizacao')

    class Meta:
        model = Sede
        fields = ("localizacao", "telefones", "endereco_eletronico")

    def get_telefones(self, obj):
        return {
            "telefone_um": obj.telefone_um,
            "telefone_dois": obj.telefone_dois,
            "telefone_tres": obj.telefone_tres
        }

    def get_localizacao(self, obj):

        return {
            "cnpj": obj.cnpj,
            "endereco": obj.endereco,
            "cep": obj.cep,
            "bairro": obj.bairro,
            "complemento": obj.complemento
        }


class EnteFederadoSerializer(hal_serializers.HalModelSerializer):

    class Meta:
        model = EnteFederado
        fields = (
            "cod_ibge",
            "nome",
            "territorio",
            "populacao",
            "idh",
            "is_municipio",
            "sigla")


class GestorSerializer(hal_serializers.HalModelSerializer):
    termo_posse_prefeito = serializers.CharField(source='termo_posse')
    nome_prefeito = serializers.CharField(source='nome')

    class Meta:
        model = Gestor
        fields = ("email_institucional", "nome_prefeito", "termo_posse_prefeito")


class SistemaCulturaSerializer(hal_serializers.HalModelSerializer):
    self = HalHyperlinkedIdentityField(view_name='api:sistemacultura-detail')
    acoes_plano_trabalho = serializers.SerializerMethodField()
    ente_federado = EnteFederadoSerializer()
    governo = GestorSerializer(source='gestor')
    situacao_adesao = serializers.CharField(source='get_estado_processo_display')
    cod_situacao_adesao = serializers.CharField(source='estado_processo')
    data_adesao = serializers.DateField(source='data_publicacao_acordo')
    conselho = ConselhoComponenteSerializer()
    sede = SedeSerializer()

    class Meta:
        model = SistemaCultura
        fields = (
            "id",
            "self",
            "data_adesao",
            "situacao_adesao",
            "cod_situacao_adesao",
            "link_publicacao_acordo",
            "conferencia_nacional",
            "acoes_plano_trabalho",
            "ente_federado",
            "governo",
            "conselho",
            "sede")

    def get_acoes_plano_trabalho(self, obj):
        planotrabalho = PlanoTrabalhoSCSerializer(instance=obj, context=self.context)
        return planotrabalho.data


class SistemaCulturaDetailSerializer(PlanoTrabalhoSCSerializer):
    self = HalHyperlinkedIdentityField(view_name='api:planotrabalho-detail')
    sistema_cultura_local = \
        HalHyperlinkedIdentityField(view_name='api:sistemacultura-detail')

    class Meta:
        model = SistemaCultura
        fields = (
            "self",
            "id",
            "criacao_lei_sistema",
            "criacao_orgao_gestor",
            "criacao_conselho_cultural_ata",
            "criacao_conselho_cultural_lei",
            "criacao_plano_cultura",
            "criacao_plano_metas",
            "criacao_fundo_cultura_cnpj",
            "sistema_cultura_local"
        )

    def to_representation(self, instance):
        context = super(SistemaCulturaDetailSerializer, self).\
            to_representation(instance)
        embedded = context.pop('_embedded')

        responseContext = context.copy()
        responseContext.update(embedded)

        return responseContext
