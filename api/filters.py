import rest_framework_filters as filters

from planotrabalho.models import PlanoTrabalho
from adesao.models import Municipio


class MunicipioFilter(filters.FilterSet):
    estado_sigla = filters.CharFilter(name='estado__sigla', lookup_expr='iexact')
    nome_municipio = filters.CharFilter(name='cidade__nome_municipio', lookup_expr='iexact')
    situacao_adesao = filters.CharFilter(name='usuario__estado_processo',
                                         lookup_expr='istartswith')
    data_adesao = filters.DateFilter(name='usuario__data_publicacao_acordo')
    data_adesao_min = filters.DateFilter(name='usuario__data_publicacao_acordo', lookup_expr=('gte'))
    data_adesao_max = filters.DateFilter(name='usuario__data_publicacao_acordo', lookup_expr=('lte'))
    municipal = filters.BooleanFilter(name='cidade__nome_municipio', method='municipios_filter')
    estadual = filters.BooleanFilter(name='cidade__nome_municipio', method='municipios_filter')

    def municipios_filter(self, qs, name, value):
        isnull = not value

        if 'estadual' in self.data.keys():
            isnull = value

        lookup_expr = name + '__isnull'

        return qs.filter(**{lookup_expr: isnull})

    class Meta:
        model = Municipio
        fields = {'id', 'cnpj_prefeitura', 'data_adesao',
                  'data_adesao_min', 'data_adesao_max'}


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
                                            name='usuario__municipio',
                                            queryset=Municipio.objects.all())

    class Meta:
        model = PlanoTrabalho
        fields = {'id'}
