import pytest
import random
import datetime

from rest_framework import status
from model_mommy import mommy

from planotrabalho.models import SituacoesArquivoPlano
from adesao.models import LISTA_ESTADOS_PROCESSO
from planotrabalho.forms import SETORIAIS
from planotrabalho.models import SITUACAO_CONSELHEIRO

pytestmark = pytest.mark.django_db

url_sistemadeculturalocal = '/api/v1/sistemadeculturalocal/'
url_acoesplanotrabalho = '/api/v1/acoesplanotrabalho/'


@pytest.fixture
def situacoes():
    """Cria situações dos arquivos do Plano Trabalho enviados no banco de testes"""
    situacoes = (
        (0, 'Em preenchimento'),
        (1, 'Avaliando anexo'),
        (2, 'Concluída'),
        (3, 'Arquivo aprovado com ressalvas'),
        (4, 'Arquivo danificado'),
        (5, 'Arquivo incompleto'),
        (6, 'Arquivo incorreto')
    )

    for situacao in situacoes:
        SituacoesArquivoPlano.objects.create(id=situacao[0], descricao=situacao[1])

    return SituacoesArquivoPlano.objects.all()


@pytest.fixture
def plano_trabalho():
    conselho_cultural = mommy.make('ConselhoCultural')
    fundo_cultura = mommy.make('FundoCultura')
    plano_cultura = mommy.make('PlanoCultura')
    lei_sistema = mommy.make('CriacaoSistema')
    orgao_gestor = mommy.make('OrgaoGestor')
    mommy.make('Conselheiro', conselho=conselho_cultural)
    plano_trabalho = mommy.make('PlanoTrabalho',
                                conselho_cultural=conselho_cultural,
                                fundo_cultura=fundo_cultura,
                                criacao_sistema=lei_sistema,
                                orgao_gestor=orgao_gestor,
                                plano_cultura=plano_cultura)

    return plano_trabalho


@pytest.fixture
def entes_municipais_estaduais():
    estadual = mommy.make('Municipio')
    cidade = mommy.make('Cidade')
    municipio = mommy.make('Municipio', cidade=cidade)

    yield estadual, municipio

    estadual.delete()
    municipio.delete()

@pytest.fixture
def sistema_de_cultura(plano_trabalho):
    municipio = mommy.make('Municipio')
    mommy.make('Usuario', municipio=municipio, plano_trabalho=plano_trabalho,
               data_publicacao_acordo=datetime.date.today())

    return municipio


def test_municipios_list_endpoint_returning_200_OK(client):

    request = client.get(url_sistemadeculturalocal)

    assert request.status_code == status.HTTP_200_OK


def test_URL_sistema_cultura_local_retorna_10_sistemas(client):

    mommy.make('Municipio', _quantity=12)

    request = client.get(url_sistemadeculturalocal,
                         content_type="application/hal+json")

    assert isinstance(request.data["_embedded"]["items"], list)
    assert len(request.data["_embedded"]["items"]) == 10


def test_404_recupera_ID_sistema_cultura_local(client):

    url = url_sistemadeculturalocal + '45/'

    request = client.get(url, content_type="application/hal+json")

    assert request.status_code == status.HTTP_404_NOT_FOUND


def test_recupera_ID_param_sistema_cultura_local(client, sistema_de_cultura):

    municipio_id = '{}/'.format(sistema_de_cultura.id)
    url = url_sistemadeculturalocal + municipio_id

    request = client.get(url, content_type="application/hal+json")

    assert request.status_code == status.HTTP_200_OK
    assert request.data["id"] == sistema_de_cultura.id


def test_entidades_principais_sistema_cultura_local(client, sistema_de_cultura):

    municipio_id = '{}/'.format(sistema_de_cultura.id)
    url = url_sistemadeculturalocal + municipio_id

    request = client.get(url, content_type="application/hal+json")

    entidades = set(["governo", "ente_federado", "conselho",
                     "_embedded", "situacao_adesao", "data_adesao",
                     "_links", "id"])

    assert entidades.symmetric_difference(request.data) == set()


def test_campos_do_objeto_governo_ao_retornar_sistema_cultura_local(client, sistema_de_cultura):

    municipio_id = '{}/'.format(sistema_de_cultura.id)
    url = url_sistemadeculturalocal + municipio_id

    request = client.get(url, content_type="application/hal+json")

    campos = set(["nome_prefeito", "email_institucional_prefeito",
                  "termo_posse_prefeito"])

    assert campos.symmetric_difference(request.data["governo"]) == set()


def test_campos_do_objeto_ente_federado_ao_retornar_sistema_cultura_local(client, sistema_de_cultura):

    municipio_id = '{}/'.format(sistema_de_cultura.id)
    url = url_sistemadeculturalocal + municipio_id

    request = client.get(url, content_type="application/hal+json")

    campos = set(["cnpj_prefeitura", "endereco_eletronico", "telefones", "localizacao"])

    assert campos.symmetric_difference(request.data["ente_federado"]) == set()


def test_campos_do_objeto_embedded_ao_retornar_sistema_cultura_local(client, sistema_de_cultura):

    municipio_id = '{}/'.format(sistema_de_cultura.id)
    url = url_sistemadeculturalocal + municipio_id

    request = client.get(url, content_type="application/hal+json")

    campos = set(["acoes_plano_trabalho"])

    assert campos.symmetric_difference(request.data["_embedded"]) == set()


def test_campos_do_objeto_conselho_ao_retornar_sistema_cultura_local(client, sistema_de_cultura):

    municipio_id = '{}/'.format(sistema_de_cultura.id)
    url = url_sistemadeculturalocal + municipio_id

    request = client.get(url, content_type="application/hal+json")

    campos = set(["conselheiros"])

    assert campos.symmetric_difference(request.data["conselho"]) == set()


def test_planotrabalho_list_endpoint_returning_200_OK(client):

    request = client.get(url_acoesplanotrabalho)

    assert request.status_code == status.HTTP_200_OK


def test_planotrabalho_list_retorna_lista_com_10(client):

    mommy.make('PlanoTrabalho', 13)

    request = client.get(url_acoesplanotrabalho,
                         content_type="application/hal+json")

    assert isinstance(request.data["_embedded"]["items"], list)
    assert len(request.data["_embedded"]["items"]) == 10


def test_acoesplanotrabalho_retorna_404_para_id_nao_valido(client):

    url = url_acoesplanotrabalho + '55/'

    request = client.get(url, content_type="application/hal+json")

    assert request.status_code == status.HTTP_404_NOT_FOUND


def test_acoesplanotrabalho_retorna_para_id_valido(client, plano_trabalho):

    plano_trabalho_id = '{}/'.format(plano_trabalho.id)
    url = url_acoesplanotrabalho + plano_trabalho_id

    request = client.get(url, content_type="application/hal+json")

    assert request.status_code == status.HTTP_200_OK
    assert request.data["id"] == plano_trabalho.id


def test_campos_acoesplanotrabalho(client, plano_trabalho):

    plano_trabalho_id = '{}/'.format(plano_trabalho.id)
    url = url_acoesplanotrabalho + plano_trabalho_id

    request = client.get(url, content_type="application/hal+json")

    campos = set(["criacao_lei_sistema_cultura", "criacao_orgao_gestor",
                  "criacao_plano_cultura", "criacao_fundo_cultura",
                  "criacao_conselho_cultural", "_links", "id", "_embedded"])

    assert campos.symmetric_difference(request.data) == set()


def test_objeto_embedded_acoesplanotrabalho(client, plano_trabalho):

    plano_trabalho_id = '{}/'.format(plano_trabalho.id)
    url = url_acoesplanotrabalho + plano_trabalho_id

    request = client.get(url, content_type="application/hal+json")

    campos = set(["sistema_cultura_local"])

    assert campos.symmetric_difference(request.data["_embedded"]) == set()


def test_objeto_criacao_lei_sistema_cultura_acoesplanotrabalho(client, plano_trabalho):

    plano_trabalho_id = '{}/'.format(plano_trabalho.id)
    url = url_acoesplanotrabalho + plano_trabalho_id

    request = client.get(url, content_type="application/hal+json")

    campos = set(["lei_sistema_cultura", "situacao"])

    assert campos.symmetric_difference(request.data["criacao_lei_sistema_cultura"]) == set()


def test_objeto_criacao_orgao_gestor_acoesplanotrabalho(client, plano_trabalho):

    plano_trabalho_id = '{}/'.format(plano_trabalho.id)
    url = url_acoesplanotrabalho + plano_trabalho_id

    request = client.get(url, content_type="application/hal+json")

    campos = set(["relatorio_atividade_secretaria", "situacao"])

    assert campos.symmetric_difference(request.data["criacao_orgao_gestor"]) == set()


def test_objeto_criacao_plano_cultura_acoesplanotrabalho(client, plano_trabalho):

    plano_trabalho_id = '{}/'.format(plano_trabalho.id)
    url = url_acoesplanotrabalho + plano_trabalho_id

    request = client.get(url, content_type="application/hal+json")

    campos = set(["relatorio_diretrizes_aprovadas", "minuta_preparada",
                  "ata_reuniao_aprovacao_plano", "ata_votacao_projeto_lei",
                  "lei_plano_cultura", "situacao"])

    assert campos.symmetric_difference(request.data["criacao_plano_cultura"]) == set()


def test_objeto_criacao_fundo_cultura_acoesplanotrabalho(client, plano_trabalho):

    plano_trabalho_id = '{}/'.format(plano_trabalho.id)
    url = url_acoesplanotrabalho + plano_trabalho_id

    request = client.get(url, content_type="application/hal+json")

    campos = set(["cnpj_fundo_cultura", "lei_fundo_cultura", "situacao"])

    assert campos.symmetric_difference(request.data["criacao_fundo_cultura"]) == set()


def test_objeto_criacao_conselho_cultural_acoesplanotrabalho(client, plano_trabalho):

    plano_trabalho_id = '{}/'.format(plano_trabalho.id)
    url = url_acoesplanotrabalho + plano_trabalho_id

    request = client.get(url, content_type="application/hal+json")

    campos = set(["ata_regimento_aprovado", "situacao"])

    assert campos.symmetric_difference(request.data["criacao_conselho_cultural"]) == set()


def test_objeto_conselheiros_sistema_de_cultura(client, sistema_de_cultura):

    sistema_id = '{}/'.format(sistema_de_cultura.id)
    url = url_sistemadeculturalocal + sistema_id

    request = client.get(url, content_type="application/hal+json")

    campos = set(["segmento", "situacao", "data_cadastro", "email",
                  "data_situacao", "nome"])

    assert campos.symmetric_difference(request.data["conselho"]["conselheiros"][0]) == set()


def test_retorno_situacao_conselheiro(client, sistema_de_cultura):

    sistema_id = '{}/'.format(sistema_de_cultura.id)
    url = url_sistemadeculturalocal + sistema_id

    request = client.get(url, content_type="application/hal+json")

    situacao = request.data["conselho"]["conselheiros"][0]["situacao"]

    assert situacao == "Habilitado"


def test_retorno_data_adesao_sistema_de_cultura(client, sistema_de_cultura):

    sistema_id = '{}/'.format(sistema_de_cultura.id)
    url = url_sistemadeculturalocal + sistema_id

    request = client.get(url, content_type="application/hal+json")

    assert request.data["data_adesao"]
    assert request.data["data_adesao"] == str(sistema_de_cultura.usuario.data_publicacao_acordo)


""" Testes de requisições com parâmetros """


def test_retorno_maximo_de_100_objetos_sistema_de_cultura(client):

    mommy.make('Municipio', 150)
    limit_param = '?limit=150'

    url = url_sistemadeculturalocal + limit_param

    request = client.get(url, content_type="application/hal+json")

    assert len(request.data["_embedded"]["items"]) == 100


def test_retorno_maximo_de_100_objetos_acoes_plano_trabalho(client):

    mommy.make('PlanoTrabalho', 150)
    limit_param = '?limit=150'

    url = url_acoesplanotrabalho + limit_param

    request = client.get(url, content_type="application/hal+json")

    assert len(request.data["_embedded"]["items"]) == 100


def test_pesquisa_por_cnpj_prefeitura_em_sistema_de_cultura(client):

    municipio = mommy.make('Municipio', 50)
    cnpj_param = '?cnpj_prefeitura={}'.format(municipio[0].cnpj_prefeitura)

    url = url_sistemadeculturalocal + cnpj_param

    request = client.get(url, content_type="application/hal+json")

    assert len(request.data["_embedded"]["items"]) == 1
    assert request.data["_embedded"]["items"][0]["ente_federado"]["cnpj_prefeitura"] == municipio[0].cnpj_prefeitura


def test_pesquisa_por_nome_municipio_em_sistema_de_cultura(client):

    cidades = mommy.make('Cidade', 50)

    for cidade in cidades:
        mommy.make('Municipio', cidade=cidade)

    nome_municipio_param = '?nome_municipio={}'.format(cidades[0].nome_municipio)

    url = url_sistemadeculturalocal + nome_municipio_param

    request = client.get(url, content_type="application/hal+json")

    assert len(request.data["_embedded"]["items"]) == 1
    assert request.data["_embedded"]["items"][0]["ente_federado"]["localizacao"]["cidade"]["nome_municipio"] == cidades[0].nome_municipio

def test_pesquisa_por_nome_municipio_em_sistema_de_cultura_letras_maiusculas(client):

    cidades = mommy.make('Cidade', _quantity=2)

    for cidade in cidades:
        mommy.make('Municipio', cidade=cidade)

    nome_municipio_maiusculo = cidades[0].nome_municipio.upper()
    nome_municipio_param = '?nome_municipio={}'.format(nome_municipio_maiusculo)

    url = url_sistemadeculturalocal + nome_municipio_param

    request = client.get(url, content_type="application/hal+json")

    assert len(request.data["_embedded"]["items"]) == 1
    assert request.data["_embedded"]["items"][0]["ente_federado"]["localizacao"]["cidade"]["nome_municipio"] == cidades[0].nome_municipio

def test_pesquisa_por_nome_municipio_em_sistema_de_cultura_letras_minusculas(client):

    cidades = mommy.make('Cidade', _quantity=2)

    for cidade in cidades:
        mommy.make('Municipio', cidade=cidade)

    nome_municipio_minusculo = cidades[0].nome_municipio.lower()
    nome_municipio_param = '?nome_municipio={}'.format(nome_municipio_minusculo)

    url = url_sistemadeculturalocal + nome_municipio_param

    request = client.get(url, content_type="application/hal+json")

    assert len(request.data["_embedded"]["items"]) == 1
    assert request.data["_embedded"]["items"][0]["ente_federado"]["localizacao"]["cidade"]["nome_municipio"] == cidades[0].nome_municipio

def test_pesquisa_por_estado_sigla_em_sistema_de_cultura(client):

    municipios = mommy.make('Municipio', 50)

    estado_sigla_param = '?estado_sigla={}'.format(municipios[0].estado.sigla)

    url = url_sistemadeculturalocal + estado_sigla_param

    request = client.get(url, content_type="application/hal+json")

    for municipio in request.data["_embedded"]["items"]:
        assert municipio["ente_federado"]["localizacao"]["estado"]["sigla"] == municipios[0].estado.sigla

def test_pesquisa_por_estado_sigla_minuscula_em_sistema_de_cultura(client):

    municipios = mommy.make('Municipio', _quantity=2)

    estado_sigla_minuscula = municipios[0].estado.sigla.lower()
    estado_sigla_param = '?estado_sigla={}'.format(estado_sigla_minuscula)

    url = url_sistemadeculturalocal + estado_sigla_param

    request = client.get(url, content_type="application/hal+json")

    for municipio in request.data["_embedded"]["items"]:
        assert municipio["ente_federado"]["localizacao"]["estado"]["sigla"] == municipios[0].estado.sigla

def test_pesquisa_por_estado_sigla_maiuscula_em_sistema_de_cultura(client):

    municipios = mommy.make('Municipio', _quantity=2)

    estado_sigla_maiuscula = municipios[0].estado.sigla.upper()
    estado_sigla_param = '?estado_sigla={}'.format(estado_sigla_maiuscula)

    url = url_sistemadeculturalocal + estado_sigla_param

    request = client.get(url, content_type="application/hal+json")

    for municipio in request.data["_embedded"]["items"]:
        assert municipio["ente_federado"]["localizacao"]["estado"]["sigla"] == municipios[0].estado.sigla

def test_pesquisa_por_situacao_adesao_1_em_sistema_de_cultura(client):

    municipios = mommy.make('Municipio', 50)
    estados_processo = ['1', '2', '3', '4', '5', '6']

    for municipio in municipios:
        mommy.make('Usuario', municipio=municipio,
                   estado_processo=random.choice(estados_processo))

    situacao_adesao_param = '?situacao_adesao=1'
    url = url_sistemadeculturalocal + situacao_adesao_param

    request = client.get(url, content_type="application/hal+json")

    for municipio in request.data["_embedded"]["items"]:
        assert municipio["situacao_adesao"]["situacao_adesao"] == 'Aguardando envio da documentação'


def test_pesquisa_por_situacao_adesao_2_em_sistema_de_cultura(client):

    municipios = mommy.make('Municipio', 50)
    estados_processo = ['1', '2', '3', '4', '5', '6']

    for municipio in municipios:
        mommy.make('Usuario', municipio=municipio,
                   estado_processo=random.choice(estados_processo))

    situacao_adesao_param = '?situacao_adesao=2'
    url = url_sistemadeculturalocal + situacao_adesao_param

    request = client.get(url, content_type="application/hal+json")

    for municipio in request.data["_embedded"]["items"]:
        assert municipio["situacao_adesao"]["situacao_adesao"] == 'Documentação Recebida - Aguarda Análise'


def test_pesquisa_por_situacao_adesao_3_em_sistema_de_cultura(client):

    municipios = mommy.make('Municipio', 50)
    estados_processo = ['1', '2', '3', '4', '5', '6']

    for municipio in municipios:
        mommy.make('Usuario', municipio=municipio,
                   estado_processo=random.choice(estados_processo))

    situacao_adesao_param = '?situacao_adesao=3'
    url = url_sistemadeculturalocal + situacao_adesao_param

    request = client.get(url, content_type="application/hal+json")

    for municipio in request.data["_embedded"]["items"]:
        assert municipio["situacao_adesao"]["situacao_adesao"] == 'Diligência Documental'


def test_pesquisa_por_situacao_adesao_4_em_sistema_de_cultura(client):

    municipios = mommy.make('Municipio', 50)
    estados_processo = ['1', '2', '3', '4', '5', '6']

    for municipio in municipios:
        mommy.make('Usuario', municipio=municipio,
                   estado_processo=random.choice(estados_processo))

    situacao_adesao_param = '?situacao_adesao=4'
    url = url_sistemadeculturalocal + situacao_adesao_param

    request = client.get(url, content_type="application/hal+json")

    for municipio in request.data["_embedded"]["items"]:
        assert municipio["situacao_adesao"]["situacao_adesao"] == 'Encaminhado para assinatura do Secretário SAI'


def test_pesquisa_por_situacao_adesao_5_em_sistema_de_cultura(client):

    municipios = mommy.make('Municipio', 50)
    estados_processo = ['1', '2', '3', '4', '5', '6']

    for municipio in municipios:
        mommy.make('Usuario', municipio=municipio,
                   estado_processo=random.choice(estados_processo))

    situacao_adesao_param = '?situacao_adesao=5'
    url = url_sistemadeculturalocal + situacao_adesao_param

    request = client.get(url, content_type="application/hal+json")

    for municipio in request.data["_embedded"]["items"]:
        assert municipio["situacao_adesao"]["situacao_adesao"] == 'Aguarda Publicação no DOU'


def test_pesquisa_por_situacao_adesao_6_em_sistema_de_cultura(client):

    municipios = mommy.make('Municipio', 50)
    estados_processo = ['1', '2', '3', '4', '5', '6']

    for municipio in municipios:
        mommy.make('Usuario', municipio=municipio,
                   estado_processo=random.choice(estados_processo))

    situacao_adesao_param = '?situacao_adesao=6'
    url = url_sistemadeculturalocal + situacao_adesao_param

    request = client.get(url, content_type="application/hal+json")

    for municipio in request.data["_embedded"]["items"]:
        assert municipio["situacao_adesao"]["situacao_adesao"] == 'Publicado no DOU'


def test_pesquisa_data_adesao_sistema_de_cultura(client, sistema_de_cultura):
    mommy.make('Municipio', 50)

    data_param = '?data_adesao={}'.format(sistema_de_cultura.usuario.data_publicacao_acordo)
    url = url_sistemadeculturalocal + data_param

    request = client.get(url, content_type="application/hal+json")

    assert len(request.data["_embedded"]["items"]) == 1
    assert request.data["_embedded"]["items"][0]["data_adesao"] == str(sistema_de_cultura.usuario.data_publicacao_acordo)


def test_pesquisa_range_data_adesao_sistema_de_cultura(client, sistema_de_cultura):
    municipios = mommy.make('Municipio', 50)
    old_date = datetime.date.today() - datetime.timedelta(2)
    actual_date = sistema_de_cultura.usuario.data_publicacao_acordo

    mommy.make('Usuario', municipio=municipios[0],
               data_publicacao_acordo=old_date)

    mommy.make('Usuario', municipio=municipios[1],
               data_publicacao_acordo=actual_date + datetime.timedelta(4))

    mommy.make('Usuario', municipio=municipios[2],
               data_publicacao_acordo=actual_date + datetime.timedelta(5))

    data_range_param = '?data_adesao_min={}&data_adesao_max={}'.format(old_date, actual_date)
    url = url_sistemadeculturalocal + data_range_param

    request = client.get(url, content_type="application/hal+json")

    data = request.data["_embedded"]["items"]

    assert len(data) == 2
    assert data[0]["data_adesao"] == str(old_date)
    assert data[1]["data_adesao"] == str(actual_date)


""" Testa requisição do tipo OPTIONS """


def test_200_options_sistema_de_cultura(client):
    request = client.options(url_sistemadeculturalocal)

    assert request.status_code == 200


def test_choices_ente_federado_sistema_de_cultura(client):
    request = client.options(url_sistemadeculturalocal)

    situacoes_list = []

    for situacao in LISTA_ESTADOS_PROCESSO:
        situacoes_list.append({'id': situacao[0], 'description': situacao[1]})

    assert request.data['ente_federado']['situacao_adesao']['choices'] == situacoes_list


def test_choices_situacao_acoes_plano_trabalho(client, situacoes):
    request = client.options(url_acoesplanotrabalho)

    situacoes_list = []

    for situacao in situacoes:
        situacoes_list.append({'id': situacao.id, 'description': situacao.descricao})

    assert request.data['situacao']['choices'] == situacoes_list


def test_choices_segmento_conselheiros(client):
    request = client.options(url_sistemadeculturalocal)

    segments_list = []

    for segmento in SETORIAIS:
        segments_list.append({'id': segmento[0], 'description': segmento[1]})

    assert request.data['conselho']['segmento']['choices'] == segments_list


def test_choices_situacao_conselheiro(client):
    request = client.options(url_sistemadeculturalocal)

    situacao_list = []

    for situacao in SITUACAO_CONSELHEIRO:
        situacao_list.append({'id': situacao[0], 'description': situacao[1]})

    assert request.data['conselho']['situacao']['choices'] == situacao_list


def test_retorno_sistemas_cultura_municipios(client, entes_municipais_estaduais):
    """ Testa retorno de sistema culturas que são referentes a adesões
    de entes federados municipais """
    estado, municipio = entes_municipais_estaduais
    url = url_sistemadeculturalocal + '?municipal=true'

    response = client.get(url)
    municipio_response = response.data['_embedded']['items'][0]['ente_federado']['localizacao']['cidade']['nome_municipio']

    assert len(response.data['_embedded']['items']) == 1
    assert municipio_response == municipio.cidade.nome_municipio
 
def test_retorno_sistemas_cultura_estados(client, entes_municipais_estaduais):
    """ Testa retorno de sistema culturas que são referentes a adesões
    de entes federados estaduais """
    estadual, municipio = entes_municipais_estaduais
    url = url_sistemadeculturalocal + '?estadual=true'

    response = client.get(url)
    municipio_response = response.data['_embedded']['items'][0]['ente_federado']['localizacao']['estado']['sigla']

    assert len(response.data['_embedded']['items']) == 1
    assert municipio_response == estadual.estado.sigla
 
