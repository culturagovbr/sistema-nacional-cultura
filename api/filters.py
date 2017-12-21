from rest_framework import viewsets
import rest_framework_filters as filters
from planotrabalho.models import * 
from adesao.models import Municipio, Cidade, Usuario, Uf 

# Classes para filtros de pesquisa

class MunicipioFilter(filters.FilterSet):
    estado_sigla = filters.CharFilter(name='estado__sigla')
    nome_municipio = filters.CharFilter(name='cidade__nome_municipio')
    class Meta:
        model = Municipio
        fields = {'id','cnpj_prefeitura'}        

class SituacoesFilter(filters.FilterSet):
    class Meta:
        model = SituacoesArquivoPlano
        fields = {'descricao': ['istartswith'],}

class PlanoTrabalhoFilter(filters.FilterSet):
    situacao_conselho_descricao = filters.CharFilter(name='conselho_cultural__situacao_ata__descricao',
            lookup_expr='istartswith')
    situacao_conselho_id = filters.NumberFilter(name='conselho_cultural__situacao_ata__id')

    situacao_orgao_descricao = filters.CharFilter(name='orgao_gestor__situacao_relatorio_secretaria__descricao',
            lookup_expr='istartswith')
    situacao_orgao_id = filters.NumberFilter(name='orgao_gestor__situacao_relatorio_secretaria__id')

    situacao_lei_descricao = filters.CharFilter(name='criacao_sistema__situacao_lei_sistema__descricao',
            lookup_expr='istartswith')
    situacao_lei_id = filters.CharFilter(name='criacao_sistema__situacao_lei_sistema__id')

    situacao_fundo_descricao = filters.CharFilter(name='fundo_cultura__situacao_lei_plano__descricao',
            lookup_expr='istartswith')
    situacao_fundo_id = filters.NumberFilter(name='fundo_cultura__situacao_lei_plano__descricao__id')

    situacao_plano_descricao = filters.CharFilter(name='plano_cultura__situacao_lei_plano__descricao',
            lookup_expr='istartswith')
    situacao_plano_id = filters.NumberFilter(name='plano_cultura__situacao_lei_plano__descricao__id')

    sistema_cultura = filters.RelatedFilter(MunicipioFilter,
        name='usuario__municipio', queryset=Municipio.objects.all())
    class Meta:
        model = PlanoTrabalho
        fields = {'id'}   
 
