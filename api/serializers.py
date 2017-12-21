from rest_framework import serializers

from drf_hal_json import serializers as hal_serializers

from adesao.models import Municipio, Uf, Cidade, Usuario
from planotrabalho.models import (PlanoTrabalho, CriacaoSistema, OrgaoGestor,
ConselhoCultural, FundoCultura, PlanoCultura, Conselheiro, SituacoesArquivoPlano)
from drf_hal_json.fields import HalHyperlinkedRelatedField, HalContributeToLinkField
import json

# Criacao do Sistema 
class CriacaoSistemaSerializer(hal_serializers.HalModelSerializer):
    situacao = serializers.ReadOnlyField(
            source = 'situacao_lei_sistema.descricao')
    class Meta:
        model = CriacaoSistema
        fields = ('lei_sistema_cultura', 'situacao')

# Orgão gestor
class OrgaoGestorSerializer(hal_serializers.HalModelSerializer):
    situacao = serializers.ReadOnlyField(source = 'situacao_relatorio_secretaria.descricao')

    class Meta:
        model = OrgaoGestor
        fields = ('relatorio_atividade_secretaria',
                  'situacao')

# Conselho Cultural
class ConselhoCulturalSerializer(hal_serializers.HalModelSerializer):
    situacao = serializers.ReadOnlyField(
            source = 'situacao_ata.descricao')

    class Meta:
        model = ConselhoCultural
        fields = ('ata_regimento_aprovado','situacao')

# Conselheiro
class ConselheiroSerializer(hal_serializers.HalModelSerializer):
    class Meta:
        model = Conselheiro
        fields = ['nome','segmento','email','situacao', 'data_cadastro', 'data_situacao']


# Fundo cultural
class FundoCulturaSerializer(hal_serializers.HalModelSerializer):
    situacao = serializers.ReadOnlyField(
            source = 'situacao_lei_plano.descricao')
    class Meta:
        model = FundoCultura
        fields = ('cnpj_fundo_cultura','lei_fundo_cultura',
                  'situacao')

# Plano Cultural
class PlanoCulturaSerializer(hal_serializers.HalModelSerializer):
    situacao = serializers.ReadOnlyField(
            source = 'situacao_lei_plano.descricao')
    class Meta:
        model = PlanoCultura
        fields = ('relatorio_diretrizes_aprovadas', 'minuta_preparada',
                  'ata_reuniao_aprovacao_plano', 'ata_votacao_projeto_lei',
                  'lei_plano_cultura','situacao')

# Plano de Trabalho
class PlanoTrabalhoSerializer(hal_serializers.HalModelSerializer):
    criacao_lei_sistema_cultura = serializers.SerializerMethodField(source= 'criacao_sistema')
    criacao_orgao_gestor = serializers.SerializerMethodField(source= 'orgao_gestor')
    criacao_plano_cultura = serializers.SerializerMethodField(source= 'plano_cultura')
    criacao_fundo_cultura = serializers.SerializerMethodField(source= 'fundo_cultura')
    criacao_conselho_cultural = serializers.SerializerMethodField(source= 'conselho_cultural')

    class Meta:
        model = PlanoTrabalho
        fields = ('id','self','criacao_lei_sistema_cultura','criacao_orgao_gestor','criacao_conselho_cultural',
                  'criacao_fundo_cultura','criacao_plano_cultura')

    def get_criacao_orgao_gestor(self, obj):
        if obj.orgao_gestor is not None:
            serializer = OrgaoGestorSerializer(obj.orgao_gestor)
            return serializer.data
        else:
            return None

    def get_criacao_plano_cultura(self, obj):
        if obj.plano_cultura is not None:
            serializer = PlanoCulturaSerializer(obj.plano_cultura)
            return serializer.data
        else:
            return None

    def get_criacao_fundo_cultura(self, obj):
        if obj.fundo_cultura is not None:
            serializer = FundoCulturaSerializer(obj.fundo_cultura)
            return serializer.data
        else:
            return None

    def get_criacao_lei_sistema_cultura(self, obj):
        if obj.criacao_sistema is not None:
            serializer = CriacaoSistemaSerializer(obj.criacao_sistema)
            return serializer.data
        else:
            return None

    def get_criacao_conselho_cultural(self, obj):
        if obj.conselho_cultural is not None:
            serializer = ConselhoCulturalSerializer(obj.conselho_cultural)
            return serializer.data
        else:
            return None

# Usuario
class UsuarioSerializer(hal_serializers.HalModelSerializer):
    #plano_trabalho = PlanoTrabalhoSerializer()
    #municipio = serializers.ReadOnlyField(source = 'municipio.cidade.nome_municipio')
    responsavel = serializers.ReadOnlyField(source = 'responsavel.nome_responsavel')
    class Meta:
        model = Usuario
        fields = ('responsavel','estado_processo',
                  'data_publicacao_acordo','plano_trabalho')
    
# Cidade        
class CidadeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cidade
        fields = ('codigo_ibge', 'nome_municipio')
# UF
class UfSerializer(serializers.ModelSerializer):
    class Meta:
        model = Uf 
        fields = ('codigo_ibge', 'sigla')

# Municipio
class MunicipioSerializer(hal_serializers.HalModelSerializer):
    ente_federado = serializers.SerializerMethodField() 
    governo = serializers.SerializerMethodField()
    conselho = serializers.SerializerMethodField()
    _embedded = serializers.SerializerMethodField(method_name='get_embedded')
    situacao_adesao = serializers.SerializerMethodField()
    
    class Meta:
        model = Municipio
        fields = ('id','self','_embedded','ente_federado','governo','conselho', 'situacao_adesao',)

    # Retornando a lista de conselheiros do ConselhoCultural
    def get_conselho(self, obj):

        try:
            conselho = obj.usuario.plano_trabalho.conselho_cultural
            conselheiros = conselho.conselheiro_set.filter(conselho_id=conselho)
        except AttributeError:
            return None

        lista = list(range(len(conselheiros)))

        for i in range(len(conselheiros)):
            while i <= len(conselheiros):
                serializer = ConselheiroSerializer(conselheiros[i])
                lista[i] = serializer.data
                break

        if conselheiros is None:
            return None

        else:
            return  ({'conselheiros': lista})

    # Retorna recursos embedded seguinto o padrão hal
    def get_embedded(self,obj):
        embedded = ({'acoes_plano_trabalho':self.get_acoes_plano_trabalho(obj=obj)})

        return embedded


    # Retorna o plano de trabalho do municipio
    def get_acoes_plano_trabalho(self,obj):

        # Checa se existe usuário atrelado ao muncipio
        try: 
            plano_trabalho = obj.usuario.plano_trabalho
        except Usuario.DoesNotExist:
            return None

        # Checa se o usuario tem um plano de trabalho válido
        if(plano_trabalho is None):
            return None

        # Request Context
        context = {}
        context['request'] = self.context['request']
        serializer = PlanoTrabalhoSerializer(instance=plano_trabalho,context=context)

        return serializer.data 

    # Estrutura dados no objeto ente_federado
    def get_ente_federado(self,obj):
        localizacao = Localizacao(estado=obj.estado, cidade=obj.cidade,
                cep=obj.cep, bairro=obj.bairro, endereco=obj.endereco, complemento=obj.complemento)
        telefones = Telefones(telefone_um=obj.telefone_um, telefone_dois=obj.telefone_dois,
                telefone_tres=obj.telefone_tres) 
        ente_federado = EnteFederado(cnpj_prefeitura=obj.cnpj_prefeitura,localizacao=localizacao,
                endereco_eletronico=obj.endereco_eletronico, telefones=telefones)
        serializer = EnteFederadoSerializer(ente_federado)

        return serializer.data 

    # Estrutura dados no objeto governo
    def get_governo(self,obj):
        governo = Governo(nome_prefeito=obj.nome_prefeito,
                email_institucional_prefeito=obj.email_institucional_prefeito,
                termo_posse_prefeito=obj.termo_posse_prefeito)
        serializer = GovernoSerializer(governo)
        
        return serializer.data
    
    def get_situacao_adesao(self,obj):
        try:
            processo = obj.usuario.get_estado_processo_display()
            serializer = {'situacao_adesao': processo}
        except AttributeError:
            serializer = None
        return serializer
        

# Classes para estruturar os objetos de adesoes
class EnteFederado(object):
    def __init__(self, cnpj_prefeitura, localizacao, endereco_eletronico, telefones):
        self.cnpj_prefeitura = cnpj_prefeitura
        self.localizacao = localizacao
        self.endereco_eletronico = endereco_eletronico
        self.telefones = telefones
 
class Localizacao(object):
    def __init__(self, estado, cidade, cep, bairro, endereco, complemento):
        self.estado = estado
        self.cidade = cidade 
        self.cep = cep 
        self.bairro = bairro
        self.endereco = endereco
        self.complemento = complemento

class Telefones(object):
    def __init__(self, telefone_um, telefone_dois, telefone_tres):
        self.telefone_um = telefone_um
        self.telefone_dois = telefone_dois
        self.telefone_tres = telefone_tres

class Governo(object):
    def __init__(self, nome_prefeito, email_institucional_prefeito,
            termo_posse_prefeito):
        self.nome_prefeito = nome_prefeito
        self.email_institucional_prefeito = email_institucional_prefeito
        self.termo_posse_prefeito = termo_posse_prefeito
       
# Serializers das classes de estruturação de adesoes
class LocalizacaoSerializer(serializers.Serializer):
    estado = UfSerializer() 
    cidade = CidadeSerializer()
    cep = serializers.CharField() 
    bairro = serializers.CharField() 
    endereco = serializers.CharField() 
    complemento = serializers.CharField() 

class TelefonesSerializer(serializers.Serializer):
    telefone_um = serializers.CharField()
    telefone_dois = serializers.CharField()
    telefone_tres = serializers.CharField()

class EnteFederadoSerializer(serializers.Serializer):
    cnpj_prefeitura = serializers.CharField()
    localizacao = LocalizacaoSerializer()
    telefones = TelefonesSerializer()
    endereco_eletronico = serializers.CharField()

class GovernoSerializer(serializers.Serializer):
    nome_prefeito = serializers.CharField()
    email_institucional_prefeito = serializers.CharField()
    termo_posse_prefeito = serializers.FileField()

