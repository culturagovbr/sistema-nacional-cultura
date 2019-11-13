from rest_framework.metadata import SimpleMetadata

from adesao.models import LISTA_ESTADOS_PROCESSO
from planotrabalho.models import SituacoesArquivoPlano
from planotrabalho.forms import SETORIAIS
from planotrabalho.models import SITUACAO_CONSELHEIRO
from adesao.models import EnteFederado


class MunicipioMetadata(SimpleMetadata):

    def get_choices(self, options):
        choices_list = []

        for item in options:
            data = {'id': item[0], 'description': item[1]}
            choices_list.append(data)

        choices = {'choices': choices_list}

        return choices

    def determine_metadata(self, request, view):
        metadata = super(MunicipioMetadata, self).determine_metadata(request, view)
        metadata['name'] = 'Sistema de Cultura Local'
        metadata['ente_federado'] = {}
        metadata['conselho'] = {}

        metadata['ente_federado']['situacao_adesao'] = \
            self.get_choices(LISTA_ESTADOS_PROCESSO)
        metadata['conselho']['segmento'] = self.get_choices(SETORIAIS)
        metadata['conselho']['situacao'] = self.get_choices(SITUACAO_CONSELHEIRO)
        metadata['estado'] = self.get_choices(EnteFederado.objects.filter(
            cod_ibge__lte=53).values_list('cod_ibge', 'nome').order_by('nome'))

        return metadata


class PlanoTrabalhoMetadata(SimpleMetadata):

    def get_situacao_arquivos(self):
        situacoes = SituacoesArquivoPlano.objects.all()
        situacao_adesao = []

        for situacao in situacoes:
            data = {'id': situacao.id, 'description': situacao.descricao}
            situacao_adesao.append(data)

        choices = {'choices': situacao_adesao}

        return choices

    def determine_metadata(self, request, view):
        metadata = super(PlanoTrabalhoMetadata, self).determine_metadata(request, view)
        metadata['name'] = 'Ações do Plano de trabalho'
        metadata['situacao'] = self.get_situacao_arquivos()

        return metadata
