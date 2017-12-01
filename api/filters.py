from rest_framework import viewsets
import rest_framework_filters as filters
from planotrabalho.models import * 
from adesao.models import Municipio, Cidade, Usuario, Cidade

# from .views import *

#CLASSES DE PESQUISA 
class MunicipioFilter(filters.FilterSet):
    class Meta:
        model = Municipio
        fields = {'id'}        

class CidadeFilter(filters.FilterSet):
    municipio = filters.RelatedFilter(MunicipioFilter, name='municipio', queryset=Municipio.objects.all())
    class Meta:
        model = Cidade
        fields = {'nome_municipio'}

########

# class PlanoTrabalhoFilter(filters.FilterSet):
#     class Meta:
#         model = PlanoTrabalho
#         fields = {'id'}   

# class ConselhoCulturalFilter(filters.FilterSet):
#     planotrabalho = filters.RelatedFilter(PlanoTrabalhoFilter, name='planotrabalho', queryset=PlanoTrabalho.objects.all())
#     class Meta:
#         model = ConselhoCultural
#         fields = {'situacao_ata_id'}


# class CriacaoSistemaFilter(filters.FilterSet):
#     planotrabalho = filters.RelatedFilter(PlanoTrabalhoFilter, name='planotrabalho', queryset=PlanoTrabalho.objects.all())
#     class Meta:
#         model = CriacaoSistema
#         fields = {'situacao_lei_sistema_id'}

# class PlanoCulturaFilter(filters.FilterSet):
#     planotrabalho = filters.RelatedFilter(PlanoTrabalhoFilter, name='planotrabalho', queryset=PlanoTrabalho.objects.all())
#     class Meta:
#         model = PlanoCultura
#         fields = {'situacao_lei_plano_id'}
        
# class OrgaoGestorFilter(filters.FilterSet):
#     planotrabalho = filters.RelatedFilter(PlanoTrabalhoFilter, name='planotrabalho', queryset=PlanoTrabalho.objects.all())
#     class Meta:
#         model = OrgaoGestor
#         fields = {'situacao_relatorio_secretaria_id'}

# class FundoCulturaFilter(filters.FilterSet):
#     planotrabalho = filters.RelatedFilter(PlanoTrabalhoFilter, name='planotrabalho', queryset=PlanoTrabalho.objects.all())
#     class Meta:
#         model = FundoCultura
#         fields = {'situacao_lei_plano_id'}