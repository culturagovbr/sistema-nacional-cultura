from django.db.models import Q

from django_filters import rest_framework as filters

from adesao.models import SistemaCultura, UFS
from planotrabalho.models import Componente


class SistemaCulturaFilter(filters.FilterSet):
    ente_federado = filters.CharFilter(
        field_name='ente_federado__nome__unaccent', lookup_expr='icontains')
    estado_sigla = filters.CharFilter(method='sigla_filter')
    cnpj_prefeitura = filters.CharFilter(
        field_name='sede__cnpj', lookup_expr='contains')
    situacao_adesao = filters.CharFilter(
        field_name='estado_processo', lookup_expr='exact')
    data_adesao = filters.DateFilter(field_name='data_publicacao_acordo')
    data_adesao_min = filters.DateFilter(
        field_name='data_publicacao_acordo', lookup_expr=('gte'))
    data_adesao_max = filters.DateFilter(
        field_name='data_publicacao_acordo', lookup_expr=('lte'))
    data_componente_min = filters.DateFilter(
        field_name='data_componente_acordo', lookup_expr=('gte'),
        method='data_componente_min')
    data_componente_max = filters.DateFilter(
        field_name='data_componente_acordo', lookup_expr=('lte'),
        method='data_componente_max')
    data_lei_min = filters.DateFilter(
        field_name='legislacao__data_publicacao', lookup_expr=('gte'))
    data_lei_max = filters.DateFilter(
        field_name='legislacao__data_publicacao', lookup_expr=('lte'))
    data_orgao_gestor_min = filters.DateFilter(
        field_name='orgao_gestor__data_publicacao', lookup_expr=('gte'))
    data_orgao_gestor_max = filters.DateFilter(
        field_name='orgao_gestor__data_publicacao', lookup_expr=('lte'))
    data_conselho_min = filters.DateFilter(
        field_name='conselho__data_publicacao', lookup_expr=('gte'))
    data_conselho_max = filters.DateFilter(
        field_name='conselho__data_publicacao', lookup_expr=('lte'))
    data_fundo_cultura_min = filters.DateFilter(
        field_name='fundo_cultura__data_publicacao', lookup_expr=('gte'))
    data_fundo_cultura_max = filters.DateFilter(
        field_name='fundo_cultura__data_publicacao', lookup_expr=('lte'))
    data_plano_min = filters.DateFilter(
        field_name='plano__data_publicacao', lookup_expr=('gte'))
    data_plano_max = filters.DateFilter(
        field_name='plano__data_publicacao', lookup_expr=('lte'))
    situacao_lei_sistema = filters.ModelMultipleChoiceFilter(
        queryset=Componente.objects.all(),
        field_name='legislacao__situacao',
        to_field_name='situacao'
    )
    situacao_orgao_gestor = filters.ModelMultipleChoiceFilter(
        queryset=Componente.objects.all(),
        field_name='orgao_gestor__situacao',
        to_field_name='situacao'
    )
    situacao_conselho_cultural = filters.ModelMultipleChoiceFilter(
        queryset=Componente.objects.all(),
        field_name='conselho__situacao',
        to_field_name='situacao'
    )
    situacao_fundo_cultura = filters.ModelMultipleChoiceFilter(
        queryset=Componente.objects.all(),
        field_name='fundo_cultura__situacao',
        to_field_name='situacao'
    )
    situacao_plano_cultura = filters.ModelMultipleChoiceFilter(
        queryset=Componente.objects.all(),
        field_name='plano__situacao',
        to_field_name='situacao'
    )
    municipal = filters.BooleanFilter(method='municipal_filter')
    estadual = filters.BooleanFilter(method='estadual_filter')

    class Meta:
        model = SistemaCultura
        exclude = ('oficio_cadastrador',)

    def sigla_filter(self, queryset, name, value):
        try:
            inverseUf = {value: key for key, value in UFS.items()}
            cod_ibge = inverseUf[value.upper()]
        except Exception:
            cod_ibge = value

        return queryset.filter(Q(ente_federado__cod_ibge__startswith=cod_ibge))

    def estadual_filter(self, queryset, name, value):
        pular_filtro = self.checar_filtro_municipal_estadual_ativos()
        if(pular_filtro):
            return queryset

        if value:
            queryset = queryset.filter(ente_federado__cod_ibge__lte=100)

        return queryset

    def municipal_filter(self, queryset, name, value):
        pular_filtro = self.checar_filtro_municipal_estadual_ativos()
        if(pular_filtro):
            return queryset

        if value:
            queryset = queryset.filter(ente_federado__cod_ibge__gt=100)

        return queryset

    def checar_filtro_municipal_estadual_ativos(self):
        try:
            estadual_filter = self.data.getlist('estadual')[0]
            municipal_filter = self.data.getlist('municipal')[0]

        except IndexError:
            return False

        if(estadual_filter == 'true' and municipal_filter == 'true'):
            return True

        return False


class PlanoTrabalhoFilter(SistemaCulturaFilter):
    class Meta:
        model = SistemaCultura
        exclude = ('oficio_cadastrador',)