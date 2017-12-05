from rest_framework import viewsets
import rest_framework_filters as filters
from planotrabalho.models import * 
from adesao.models import Municipio, Cidade, Usuario, Uf 

# Classes para filtros de pesquisa
class CidadeFilter(filters.FilterSet):
    class Meta:
        model = Cidade
        fields = {'nome_municipio'}

class MunicipioFilter(filters.FilterSet):
    cidade = filters.RelatedFilter(CidadeFilter, name='cidade', queryset=Cidade.objects.all())
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

class OrgaoGestorFilter(filters.FilterSet):
    situacao = filters.RelatedFilter(SituacoesFilter, 
            name='situacao_relatorio_secretaria', queryset=SituacoesArquivoPlano.objects.all())
    class Meta:
        model = OrgaoGestor
        fields = {'id',}

class PlanoTrabalhoFilter(filters.FilterSet):
    criacao_conselho_cultural= filters.RelatedFilter(ConselhoCulturalFilter, 
        name='conselho_cultural', queryset=ConselhoCultural.objects.all())
    criacao_orgao_gestor= filters.RelatedFilter(OrgaoGestorFilter, 
        name='orgao_gestor', queryset=OrgaoGestor.objects.all())
    class Meta:
        model = PlanoTrabalho
        fields = {'id'}   
 
