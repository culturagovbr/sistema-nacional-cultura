import xlsxwriter
import xlwt

from io import BytesIO

from django.http import HttpResponse
from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import filters
from rest_framework import generics

from adesao.models import SistemaCultura

from .serializers import SistemaCulturaSerializer
from .serializers import SistemaCulturaDetailSerializer
from .serializers import PlanoTrabalhoSerializer

from .filters import SistemaCulturaFilter
from .filters import PlanoTrabalhoFilter

from .metadata import MunicipioMetadata as SistemaCulturaMetadata
from .metadata import PlanoTrabalhoMetadata

from .utils import preenche_planilha


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

        queryset = self.filter_queryset(self.get_queryset())

        municipios = queryset.filter(ente_federado__cod_ibge__gt=100)
        estados = queryset.filter(ente_federado__cod_ibge__lte=100)

        response = super().list(self, request)
        response.data['municipios'] = municipios.count()
        response.data['municipios_aderidos'] = municipios.filter(
            estado_processo=6).count()
        response.data['estados'] = estados.count()
        response.data['estados_aderidos'] = estados.filter(estado_processo=6).count()

        return response

    def xls(self, request):
        queryset = self.filter_queryset(self.get_queryset())

        ids = queryset.values_list('id', flat=True)

        output = BytesIO()

        workbook = xlsxwriter.Workbook(output)
        planilha = workbook.add_worksheet("SNC")
        ultima_linha = preenche_planilha(planilha, ids)

        planilha.autofilter(0, 0, ultima_linha,43)
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
        preenche_planilha(planilha, ids)

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
