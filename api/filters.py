from rest_framework import viewsets
import rest_framework_filters as filters
from planotrabalho.models import * 
from adesao.models import Municipio, Cidade, Usuario, Uf 

# Classes para filtros de pesquisa
class UfFilter(filters.FilterSet):
    class Meta:
        model = Uf 
        fields = {'sigla'}

class CidadeFilter(filters.FilterSet):
    class Meta:
        model = Cidade
        fields = {'nome_municipio'}

class MunicipioFilter(filters.FilterSet):
    cidade = filters.RelatedFilter(CidadeFilter, name='cidade', queryset=Cidade.objects.all())
    estado = filters.RelatedFilter(UfFilter, name='estado', queryset=Uf.objects.all())
    class Meta:
        model = Municipio
        fields = {'id','cnpj_prefeitura'}        

class SituacoesFilter(filters.FilterSet):
    class Meta:
        model = SituacoesArquivoPlano
        fields = {'id','descricao',}

class ConselhoCulturalFilter(filters.FilterSet):
    situacao = filters.RelatedFilter(SituacoesFilter, name='situacao_ata', queryset=SituacoesArquivoPlano.objects.all())
    class Meta:
        model = ConselhoCultural
        fields = {'id',}

class CriacaoSistemaFilter(filters.FilterSet):
    situacao = filters.RelatedFilter(SituacoesFilter, 
            name='situacao_lei_sistema', queryset=SituacoesArquivoPlano.objects.all())
    class Meta:
        model = CriacaoSistema
        fields = {'id',}

class FundoCulturaFilter(filters.FilterSet):
    situacao = filters.RelatedFilter(SituacoesFilter, 
            name='situacao_lei_plano', queryset=SituacoesArquivoPlano.objects.all())
    class Meta:
        model = FundoCultura 
        fields = {'id',}

class PlanoCulturaFilter(filters.FilterSet):
    situacao = filters.RelatedFilter(SituacoesFilter, 
            name='situacao_lei_plano', queryset=SituacoesArquivoPlano.objects.all())
    class Meta:
        model = PlanoCultura 
        fields = {'id',}

class OrgaoGestorFilter(filters.FilterSet):
    situacao = filters.RelatedFilter(SituacoesFilter, 
            name='situacao_relatorio_secretaria', queryset=SituacoesArquivoPlano.objects.all())
    class Meta:
        model = OrgaoGestor
        fields = {'id',}

class PlanoTrabalhoFilter(filters.FilterSet):
    situacao_conselho= filters.RelatedFilter(SituacoesFilter, 
        name='conselho_cultural__situacao_ata', queryset=ConselhoCultural.objects.all())
    situacao_orgao = filters.RelatedFilter(SituacoesFilter, 
        name='orgao_gestor__situacao_relatorio_secretaria', queryset=OrgaoGestor.objects.all())
    situacao_lei = filters.RelatedFilter(SituacoesFilter, 
        name='criacao_sistema__situacao_lei_sistema', queryset=CriacaoSistema.objects.all())
    situacao_fundo = filters.RelatedFilter(SituacoesFilter,
        name='fundo_cultura__situacao_lei_plano', queryset=FundoCultura.objects.all())
    situacao_plano = filters.RelatedFilter(SituacoesFilter,
        name='plano_cultura__situacao_lei_plano', queryset=PlanoCultura.objects.all())

    sistema_cultura = filters.RelatedFilter(MunicipioFilter,
        name='usuario__municipio', queryset=Municipio.objects.all())
    class Meta:
        model = PlanoTrabalho
        fields = {'id'}   
 
