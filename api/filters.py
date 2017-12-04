from rest_framework import viewsets
import rest_framework_filters as filters
from planotrabalho.models import * 
from adesao.models import Municipio, Cidade, Usuario, Cidade

# from .views import *

# CLASSES DE PESQUISA 
class MunicipioFilter(filters.FilterSet):
    class Meta:
        model = Municipio
        fields = {'id'}        

class CidadeFilter(filters.FilterSet):
    municipio = filters.RelatedFilter(MunicipioFilter, name='municipio', queryset=Municipio.objects.all())
    class Meta:
        model = Cidade
        fields = {'nome_municipio'}

# class PlanoTrabalhoFilter(filters.FilterSet):
#     class Meta:
#         model = PlanoTrabalho
#         fields = {'id'}   

# class ConselhoCulturalFilter(filters.FilterSet):
#     planotrabalho = filters.RelatedFilter(PlanoTrabalhoFilter, name='planotrabalho', queryset=PlanoTrabalho.objects.all())
#     class Meta:
#         model = ConselhoCultural
#         fields = {'situacao_ata',}




        

