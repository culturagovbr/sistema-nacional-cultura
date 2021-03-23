import xlsxwriter
import xlwt

from io import BytesIO

from django.http import HttpResponse
from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import filters
from rest_framework import generics

from django.db.models import Q

from adesao.models import SistemaCultura

from .serializers import SistemaCulturaSerializer
from .serializers import SistemaCulturaDetailSerializer
from .serializers import PlanoTrabalhoSerializer

from .filters import SistemaCulturaFilter
from .filters import PlanoTrabalhoFilter

from .metadata import MunicipioMetadata as SistemaCulturaMetadata
from .metadata import PlanoTrabalhoMetadata

from .utils import preenche_planilha
from .utils import sistema_cultura_filtros


def swagger_index(request):
    return render(request, 'swagger/index.html')


class SistemaCulturaAPIList(generics.ListAPIView):
    queryset = SistemaCultura.sistema.all()
    serializer_class = SistemaCulturaSerializer
    metadata_class = SistemaCulturaMetadata

    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    filterset_class = SistemaCulturaFilter
    ordering_fields = ('ente_federado__nome', 'ente_federado')

    def list(self, request):
        if request.accepted_renderer.format == 'xls':
            return self.xls(request)
        if request.accepted_renderer.format == 'ods':
            return self.ods(request)

        qd = request.query_params
    
        filters = []

        for k, v in qd.items(): 
            if k.find('data_lei_max') > -1:
                filters.append('SistemaCultura.sistema.filter(Q(legislacao__situacao=2) | Q(legislacao__situacao=3))')
            if k.find('data_orgao_gestor_max') > -1:
                filters.append('SistemaCultura.sistema.filter(Q(orgao_gestor__situacao=2) | Q(orgao_gestor__situacao=3))')
            if k.find('data_conselho_lei_max') > -1:
                filters.append('SistemaCultura.sistema.filter(Q(conselho__situacao=2) | Q(conselho__situacao=3))')
            if k.find('data_fundo_cultura_max') > -1:
                filters.append('SistemaCultura.sistema.filter(Q(fundo_cultura__situacao=2) | Q(fundo_cultura__situacao=3))')
            if k.find('data_plano_max') > -1:
                filters.append('SistemaCultura.sistema.filter(Q(plano__situacao=2) | Q(plano__situacao=3))')

        command_eval = 'SistemaCultura.sistema.filter(Q(ente_federado__isnull=False)) ' 

        for cmd in filters:
            command_eval = command_eval + ' & ' + cmd 
    
        sistemaCultura = eval(command_eval) 

        #sistemaCultura = sistema_cultura_filtros( request, [])

        queryset = self.filter_queryset(sistemaCultura)

        municipios = queryset.filter(ente_federado__cod_ibge__gt=100)
        estados = queryset.filter(ente_federado__cod_ibge__lte=100)

        response = super().list(self, request)
        if request.GET['municipal'] :
            response.data['municipios'] = municipios.count()
            response.data['municipios_aderidos'] = municipios.filter(estado_processo=6).count()
        else :
            response.data['municipios'] = 0
            response.data['municipios_aderidos'] = 0

        if request.GET['estadual'] :
            response.data['estados'] = estados.count()
            response.data['estados_aderidos'] = estados.filter(estado_processo=6).count()
        else :
            response.data['estados'] = 0
            response.data['estados_aderidos'] = 0
        
        return response

    def xls(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        
        ids = queryset.values_list('id', flat=True)
        output = BytesIO()

        workbook = xlsxwriter.Workbook(output)
        planilha = workbook.add_worksheet("SNC")
        ultima_linha = preenche_planilha(planilha, ids, request)

        planilha.autofilter(0, 0, ultima_linha,47)
        workbook.close()
        output.seek(0)

        response = HttpResponse(output.read(), content_type="application/vnd.ms-excel")
        response[
            "Content-Disposition"
        ] = 'attachment; filename="versnc-exportação.xls"'

        return response

    def ods(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        ids = queryset.values_list('id', flat=True)

        response = HttpResponse(
            content_type="application/vnd.oasis.opendocument.spreadsheet .ods"
        )
        response[
            "Content-Disposition"
        ] = 'attachment; filename="dados-municipios-cadastrados-snc.ods"'

        workbook = xlwt.Workbook()
        planilha = workbook.add_sheet("SNC")
        preenche_planilha(planilha, ids, request)

        workbook.save(response)

        return response


class SistemaCulturaDetail(generics.RetrieveAPIView):
    queryset = SistemaCultura.sistema.filter()
    serializer_class = SistemaCulturaSerializer


class PlanoTrabalhoList(generics.ListAPIView):
    queryset = SistemaCultura.sistema.all()
    serializer_class = PlanoTrabalhoSerializer
    metadata_class = PlanoTrabalhoMetadata

    filter_backends = (DjangoFilterBackend,)
    filterset_class = PlanoTrabalhoFilter


class PlanoTrabalhoDetail(generics.RetrieveAPIView):
    queryset = SistemaCultura.sistema.filter()
    serializer_class = SistemaCulturaDetailSerializer
