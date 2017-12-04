from rest_framework import generics
from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
import rest_framework_filters as filters
from planotrabalho.models import * 
from adesao.models import Municipio, Cidade, Usuario, Cidade
from api.serializers import MunicipioSerializer, UsuarioSerializer, PlanoTrabalhoSerializer
from .filters import *


# Swagger index page.
def swagger_index(request):
    return render(request, 'swagger/index.html')


# MUNICIPIOS
# Lista todos os municipios
class  MunicipioList(generics.ListAPIView):
    queryset = Municipio.objects.filter().order_by('-id')
    serializer_class = MunicipioSerializer
    
    filter_backends = (DjangoFilterBackend,)
    filter_class = MunicipioFilter
    # filter_fields = ('situacao_lei')
    
    def get_queryset(self):
        queryset = Municipio.objects.filter().order_by('-id')

        # Parâmetros de busca passados na requisição 
        cnpj_prefeitura = self.request.query_params.get('cnpj_prefeitura',None)
        sigla_estado = self.request.query_params.get('sigla_estado',None)
        nome_municipio = self.request.query_params.get('nome_municipio',None)

        search_params = {'cnpj_prefeitura': cnpj_prefeitura, 'estado__sigla': sigla_estado,
                         'cidade__nome_municipio': nome_municipio}

        # Lista parâmetros não vazios
        arguments = {}
        for key, value in search_params.items():
            if value:
                arguments[key] = value

        queryset = Municipio.objects.filter(**arguments)

        return queryset

# Retorna um municipio especificado pela pk
class MunicipioDetail(generics.RetrieveAPIView):
    queryset = Municipio.objects.filter().order_by('-id')
    serializer_class = MunicipioSerializer

# PLANO TRABALHO
# Lista todos os planos de trabalho 
class PlanoTrabalhoList(generics.ListAPIView):
    queryset = PlanoTrabalho.objects.filter().order_by('-id')
    serializer_class = PlanoTrabalhoSerializer 

    filter_backends = (DjangoFilterBackend,)
    # filter_class = PlanoTrabalhoFilter
    # filter_fields = ('situacao_relatorio_secretaria_id',)
    def get_queryset(self):
        queryset = PlanoTrabalho.objects.filter().order_by('-id')
        
        # Parâmetros de busca passados na requisição 
        #situacao_acao = self.request.query_params.get('situacao_acao',None)
        sistema_cultura_id = self.request.query_params.get('sistema_cultura_id',None)
        sistema_cultura_nome_municipio = self.request.query_params.get(
                'sistema_cultura_nome_municipio',None)
        sistema_cultura_cnpj_prefeitura = self.request.query_params.get(
                'sistema_cultura_cnpj_prefeitura', None)
        situacao_orgao = self.request.query_params.get('situacao_orgao',None)
        situacao_conselho = self.request.query_params.get('situacao_conselho',None)
        situacao_plano = self.request.query_params.get('situacao_plano',None)
        situacao_fundo = self.request.query_params.get('situacao_fundo',None)
        situacao_lei = self.request.query_params.get('situacao_lei',None)

        search_params = {'usuario__municipio_id': sistema_cultura_id, 
                'usuario__municipio__cidade__nome_municipio': sistema_cultura_nome_municipio,
                'usuario__municipio__cnpj_prefeitura': sistema_cultura_cnpj_prefeitura,
                'orgao_gestor__situacao_relatorio_secretaria_id':situacao_orgao,
                'plano_cultura__situacao_lei_plano_id':situacao_plano,
                'fundo_cultura__situacao_lei_plano_id':situacao_fundo,
                'criacao_sistema__situacao_lei_sistema_id':situacao_lei}
                # 'conselho_cultural__situacao_ata_id':situacao_conselho,

        # Lista parâmetros não vazios
        arguments = {}
        for key, value in search_params.items():
            if value:
                arguments[key] = value

        queryset = PlanoTrabalho.objects.filter(**arguments)

        return queryset
        
# Retorna um plano de trabalho especificado pela pk
class PlanoTrabalhoDetail(generics.RetrieveAPIView):
    queryset = PlanoTrabalho.objects.filter().order_by('-id') 
    serializer_class = PlanoTrabalhoSerializer 

# USUÁRIOS
# Lista todos os usuários
class UsuarioList(generics.ListAPIView):
    queryset = Usuario.objects.filter().order_by('-id')
    serializer_class = UsuarioSerializer
    
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('nome_usuario','municipio')

# Retorna um usuário especificado pela pk
class UsuarioDetail(generics.RetrieveAPIView):
    queryset = Usuario.objects.filter().order_by('-id') 
    serializer_class = UsuarioSerializer

