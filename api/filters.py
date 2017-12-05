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

# WIP: Não funciona
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
    criacao_conselho_cultural= filters.RelatedFilter(ConselhoCulturalFilter, 
        name='conselho_cultural', queryset=ConselhoCultural.objects.all())
    criacao_orgao_gestor = filters.RelatedFilter(OrgaoGestorFilter, 
        name='orgao_gestor', queryset=OrgaoGestor.objects.all())
    criacao_lei_sistema_cultura = filters.RelatedFilter(CriacaoSistemaFilter, 
        name='criacao_sistema', queryset=CriacaoSistema.objects.all())
    criacao_fundo_cultura = filters.RelatedFilter(FundoCulturaFilter,
        name='fundo_cultura', queryset=FundoCultura.objects.all())
    criacao_plano_cultura  = filters.RelatedFilter(PlanoCulturaFilter,
        name='plano_cultura', queryset=PlanoCultura.objects.all())

    sistema_cultura = filters.RelatedFilter(MunicipioFilter,
        name='usuario__municipio', queryset=Municipio.objects.all())
    class Meta:
        model = PlanoTrabalho
        fields = {'id'}   
 
