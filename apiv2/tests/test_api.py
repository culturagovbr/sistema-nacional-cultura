import pytest
import random
import datetime

from django.urls import reverse
from django.db.models import Q

from rest_framework import status
from model_mommy import mommy
from model_mommy.recipe import seq

from planotrabalho.models import SituacoesArquivoPlano
from adesao.models import SistemaCultura
from adesao.models import LISTA_ESTADOS_PROCESSO
from planotrabalho.forms import SETORIAIS
from planotrabalho.models import SITUACAO_CONSELHEIRO

pytestmark = pytest.mark.django_db

url_sistemadeculturalocal = reverse("api:sistemacultura-list")
url_acoesplanotrabalho = reverse("api:planotrabalho-list")


def test_municipios_list_endpoint_returning_200_OK(client):

    request = client.get(url_sistemadeculturalocal)

    assert request.status_code == status.HTTP_200_OK


def test_URL_sistema_cultura_local_retorna_10_sistemas(client):

    for ente in mommy.make('EnteFederado', _quantity=12, cod_ibge=seq(110)):
        mommy.make('SistemaCultura', ente_federado=ente)

    request = client.get(url_sistemadeculturalocal,
                         content_type="application/hal+json")

    assert isinstance(request.data["_embedded"]["items"], list)
    assert len(request.data["_embedded"]["items"]) == 10


def test_404_recupera_ID_sistema_cultura_local(client):

    url = url_sistemadeculturalocal + '45/'

    request = client.get(url, content_type="application/hal+json")

    assert request.status_code == status.HTTP_404_NOT_FOUND


def test_recupera_ID_param_sistema_cultura_local(client, sistema_cultura):

    sistema_de_cultura = SistemaCultura.sistema.first()
    sistema_id = '{}/'.format(sistema_de_cultura.id)
    url = url_sistemadeculturalocal + sistema_id

    request = client.get(url, content_type="application/hal+json")

    assert request.status_code == status.HTTP_200_OK
    assert request.data["id"] == sistema_de_cultura.id


def test_entidades_principais_sistema_cultura_local(client, sistema_cultura):

    sistema_de_cultura = SistemaCultura.sistema.first()
    sistema_id = '{}/'.format(sistema_de_cultura.id)
    url = url_sistemadeculturalocal + sistema_id

    request = client.get(url, content_type="application/hal+json")

    entidades = set(["data_adesao", "situacao_adesao",
                        "cod_situacao_adesao", "conferencia_nacional", "_embedded",
                        "_links", "id", "acoes_plano_trabalho"])

    assert entidades.symmetric_difference(request.data) == set()


def test_campos_do_objeto_governo_ao_retornar_sistema_cultura_local(client, sistema_cultura):

    sistema_de_cultura = SistemaCultura.sistema.first()
    sistema_id = '{}/'.format(sistema_de_cultura.id)
    url = url_sistemadeculturalocal + sistema_id

    request = client.get(url, content_type="application/hal+json")

    campos = set(["nome_prefeito", "email_institucional",
                  "termo_posse_prefeito"])

    assert campos.symmetric_difference(request.data["_embedded"]["governo"]) == set()


def test_campos_do_objeto_ente_federado_ao_retornar_sistema_cultura_local(client, sistema_cultura):

    sistema_de_cultura = SistemaCultura.sistema.first()
    sistema_id = '{}/'.format(sistema_de_cultura.id)
    url = url_sistemadeculturalocal + sistema_id

    request = client.get(url, content_type="application/hal+json")

    campos = set(["cod_ibge", "nome", "territorio", "populacao", "idh", "is_municipio", "sigla"])

    assert campos.symmetric_difference(request.data["_embedded"]["ente_federado"]) == set()


def test_campos_do_objeto_embedded_ao_retornar_sistema_cultura_local(client, sistema_cultura):

    sistema_de_cultura = SistemaCultura.sistema.first()
    sistema_id = '{}/'.format(sistema_de_cultura.id)
    url = url_sistemadeculturalocal + sistema_id

    request = client.get(url, content_type="application/hal+json")

    campos = set(["ente_federado", "governo", "sede", "conselho"])

    assert campos.symmetric_difference(request.data["_embedded"]) == set()


def test_campos_do_objeto_conselho_ao_retornar_sistema_cultura_local(client, sistema_cultura):

    sistema_de_cultura = SistemaCultura.sistema.first()
    sistema_id = '{}/'.format(sistema_de_cultura.id)
    url = url_sistemadeculturalocal + sistema_id

    request = client.get(url, content_type="application/hal+json")

    campos = set(["conselheiros"])

    assert campos.symmetric_difference(request.data["_embedded"]["conselho"]) == set()


def test_planotrabalho_list_endpoint_returning_200_OK(client):

    request = client.get(url_acoesplanotrabalho)

    assert request.status_code == status.HTTP_200_OK


def test_planotrabalho_list_retorna_lista_com_10(client):

    mommy.make('SistemaCultura', 13, _fill_optional=True)

    request = client.get(url_acoesplanotrabalho,
                         content_type="application/hal+json")

    assert isinstance(request.data["_embedded"]["items"], list)
    assert len(request.data["_embedded"]["items"]) == 10


def test_acoesplanotrabalho_retorna_404_para_id_nao_valido(client):

    url = url_acoesplanotrabalho + '55/'

    request = client.get(url, content_type="application/hal+json")

    assert request.status_code == status.HTTP_404_NOT_FOUND


def test_acoesplanotrabalho_retorna_para_id_valido(client, sistema_cultura):

    plano_trabalho = SistemaCultura.sistema.first()
    plano_trabalho_id = '{}/'.format(plano_trabalho.id)
    url = url_acoesplanotrabalho + plano_trabalho_id

    request = client.get(url, content_type="application/hal+json")

    assert request.status_code == status.HTTP_200_OK
    assert request.data["id"] == plano_trabalho.id


def test_campos_acoesplanotrabalho(client, sistema_cultura):

    plano_trabalho = SistemaCultura.sistema.first()
    plano_trabalho_id = '{}/'.format(plano_trabalho.id)
    url = url_acoesplanotrabalho + plano_trabalho_id

    request = client.get(url, content_type="application/hal+json")

    campos = set(["criacao_lei_sistema", "criacao_orgao_gestor",
                  "criacao_plano_cultura", "criacao_fundo_cultura",
                  "criacao_conselho_cultural", "_links", "id"])

    assert campos.symmetric_difference(request.data) == set()


def test_objeto_criacao_lei_sistema_cultura_acoesplanotrabalho(client, sistema_cultura):

    plano_trabalho = SistemaCultura.sistema.first()
    plano_trabalho_id = '{}/'.format(plano_trabalho.id)
    url = url_acoesplanotrabalho + plano_trabalho_id

    request = client.get(url, content_type="application/hal+json")

    campos = set(["cod_situacao", "situacao", "data_envio", "arquivo"])

    assert campos.symmetric_difference(request.data["criacao_lei_sistema"]) == set()


def test_objeto_criacao_orgao_gestor_acoesplanotrabalho(client, sistema_cultura):

    plano_trabalho = SistemaCultura.sistema.first()
    plano_trabalho_id = '{}/'.format(plano_trabalho.id)
    url = url_acoesplanotrabalho + plano_trabalho_id

    request = client.get(url, content_type="application/hal+json")

    campos = set(["cod_situacao", "situacao", "data_envio", "arquivo"])

    assert campos.symmetric_difference(request.data["criacao_orgao_gestor"]) == set()


def test_objeto_criacao_plano_cultura_acoesplanotrabalho(client, sistema_cultura):

    plano_trabalho = SistemaCultura.sistema.first()
    plano_trabalho_id = '{}/'.format(plano_trabalho.id)
    url = url_acoesplanotrabalho + plano_trabalho_id

    request = client.get(url, content_type="application/hal+json")

    campos = set(["cod_situacao", "situacao", "data_envio", "arquivo"])

    assert campos.symmetric_difference(request.data["criacao_plano_cultura"]) == set()


def test_objeto_criacao_fundo_cultura_acoesplanotrabalho(client, sistema_cultura):

    plano_trabalho = SistemaCultura.sistema.first()
    plano_trabalho_id = '{}/'.format(plano_trabalho.id)
    url = url_acoesplanotrabalho + plano_trabalho_id

    request = client.get(url, content_type="application/hal+json")

    campos = set(["cod_situacao", "situacao", "data_envio", "arquivo", "cnpj"])

    assert campos.symmetric_difference(request.data["criacao_fundo_cultura"]) == set()


def test_objeto_criacao_conselho_cultural_acoesplanotrabalho(client, sistema_cultura):

    plano_trabalho = SistemaCultura.sistema.first()
    plano_trabalho_id = '{}/'.format(plano_trabalho.id)
    url = url_acoesplanotrabalho + plano_trabalho_id

    request = client.get(url, content_type="application/hal+json")

    campos = set(["cod_situacao", "situacao", "data_envio", "arquivo"])

    assert campos.symmetric_difference(request.data["criacao_conselho_cultural"]) == set()


def test_objeto_conselheiros_sistema_de_cultura(client, sistema_cultura):

    sistema_de_cultura = SistemaCultura.sistema.first()
    sistema_id = '{}/'.format(sistema_de_cultura.id)
    url = url_sistemadeculturalocal + sistema_id

    request = client.get(url, content_type="application/hal+json")

    campos = set(["segmento", "situacao", "data_cadastro", "email",
                  "data_situacao", "nome", "cod_situacao"])

    assert campos.symmetric_difference(request.data["_embedded"]["conselho"]["conselheiros"][0]) == set()


def test_retorno_situacao_conselheiro(client, sistema_cultura):

    sistema_de_cultura = SistemaCultura.sistema.first()
    sistema_id = '{}/'.format(sistema_de_cultura.id)
    url = url_sistemadeculturalocal + sistema_id

    request = client.get(url, content_type="application/hal+json")

    situacao = request.data["_embedded"]["conselho"]["conselheiros"][0]["situacao"]

    assert situacao == "Habilitado"


def test_retorno_data_adesao_sistema_de_cultura(client, sistema_cultura):

    sistema_de_cultura = SistemaCultura.sistema.first()
    sistema_id = '{}/'.format(sistema_de_cultura.id)
    url = url_sistemadeculturalocal + sistema_id

    request = client.get(url, content_type="application/hal+json")

    assert request.data["data_adesao"]
    assert request.data["data_adesao"] == str(sistema_de_cultura.data_publicacao_acordo)


""" Testes de requisições com parâmetros """


def test_retorno_maximo_de_100_objetos_sistema_de_cultura(client):

    mommy.make('SistemaCultura', ente_federado__cod_ibge=seq(110), _quantity=110)
    limit_param = '?limit=150'

    url = url_sistemadeculturalocal + limit_param

    request = client.get(url, content_type="application/hal+json")

    assert len(request.data["_embedded"]["items"]) == 100


def test_pesquisa_por_cnpj_prefeitura_em_sistema_de_cultura(client):

    sistema_cultura = mommy.make('SistemaCultura', ente_federado__cod_ibge=seq(111), _quantity=2, _fill_optional=True)
    cnpj_param = '?cnpj_prefeitura={}'.format(sistema_cultura[0].sede.cnpj)

    url = url_sistemadeculturalocal + cnpj_param

    request = client.get(url, content_type="application/hal+json")

    assert len(request.data["_embedded"]["items"]) == 1
    assert request.data["_embedded"]["items"][0]["_embedded"]["sede"]["localizacao"]["cnpj"] == sistema_cultura[0].sede.cnpj


def test_pesquisa_por_nome_municipio_em_sistema_de_cultura(client):

    sistema_cultura = mommy.make('SistemaCultura', ente_federado__cod_ibge=seq(
        111), _quantity=2, _fill_optional=True)

    nome_ente_param = '?ente_federado={}'.format(
        sistema_cultura[0].ente_federado.nome)

    url = url_sistemadeculturalocal + nome_ente_param

    request = client.get(url, content_type="application/hal+json")

    assert len(request.data["_embedded"]["items"]) == 1
    assert request.data["_embedded"]["items"][0]["_embedded"]["ente_federado"]["nome"] == sistema_cultura[0].ente_federado.nome

def test_pesquisa_por_nome_municipio_em_sistema_de_cultura_letras_maiusculas(client):

    sistema_cultura = mommy.make('SistemaCultura', ente_federado__cod_ibge=seq(
        111), _quantity=2, _fill_optional=True)

    nome_ente_maiusculo = sistema_cultura[0].ente_federado.nome.upper()
    nome_ente_param = '?ente_federado={}'.format(nome_ente_maiusculo)

    url = url_sistemadeculturalocal + nome_ente_param

    request = client.get(url, content_type="application/hal+json")

    assert len(request.data["_embedded"]["items"]) == 1
    assert request.data["_embedded"]["items"][0]["_embedded"]["ente_federado"]["nome"] == sistema_cultura[0].ente_federado.nome

def test_pesquisa_por_nome_municipio_em_sistema_de_cultura_letras_minusculas(client):

    sistema_cultura = mommy.make('SistemaCultura', ente_federado__cod_ibge=seq(
        111), _quantity=2, _fill_optional=True)

    nome_ente_minusculo = sistema_cultura[0].ente_federado.nome.lower()
    nome_ente_param = '?ente_federado={}'.format(nome_ente_minusculo)

    url = url_sistemadeculturalocal + nome_ente_param

    request = client.get(url, content_type="application/hal+json")

    assert len(request.data["_embedded"]["items"]) == 1
    assert request.data["_embedded"]["items"][0]["_embedded"]["ente_federado"]["nome"] == sistema_cultura[0].ente_federado.nome


def test_pesquisa_por_estado_sigla_em_sistema_de_cultura(client):

    municipios = mommy.make('Municipio', _quantity=2)

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

    municipios = mommy.make('Municipio', _quantity=2)
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

    municipios = mommy.make('Municipio', _quantity=2)
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

    municipios = mommy.make('Municipio', _quantity=2)
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

    municipios = mommy.make('Municipio', _quantity=2)
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

    municipios = mommy.make('Municipio', _quantity=2)
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

    municipios = mommy.make('Municipio', _quantity=5)
    estados_processo = ['1', '2', '3', '4', '5', '6']

    for municipio in municipios:
        mommy.make('Usuario', municipio=municipio,
                   estado_processo=random.choice(estados_processo))

    situacao_adesao_param = '?situacao_adesao=6'
    url = url_sistemadeculturalocal + situacao_adesao_param

    request = client.get(url, content_type="application/hal+json")

    for municipio in request.data["_embedded"]["items"]:
        assert municipio["situacao_adesao"]["situacao_adesao"] == 'Publicado no DOU'


def test_pesquisa_data_adesao_sistema_de_cultura(client):
    mommy.make('SistemaCultura', _quantity=5, ente_federado__cod_ibge=seq(110),
               data_publicacao_acordo=seq(datetime.date(2018, 12, 21),
               datetime.timedelta(days=1)), _fill_optional=True)
    sistema_de_cultura = SistemaCultura.sistema.first()

    data_param = '?data_adesao={}'.format(sistema_de_cultura.data_publicacao_acordo)
    url = url_sistemadeculturalocal + data_param

    request = client.get(url, content_type="application/hal+json")

    assert len(request.data["_embedded"]["items"]) == 1
    assert request.data["_embedded"]["items"][0]["data_adesao"] == str(sistema_de_cultura.data_publicacao_acordo)


def test_pesquisa_range_data_adesao_sistema_de_cultura(client, sistema_cultura):
    sistema_de_cultura = SistemaCultura.sistema.first()
    old_date = datetime.date.today() - datetime.timedelta(2)
    actual_date = sistema_de_cultura.data_publicacao_acordo

    mommy.make('SistemaCultura', ente_federado__cod_ibge=111, data_publicacao_acordo=old_date)
    mommy.make('SistemaCultura', ente_federado__cod_ibge=112, data_publicacao_acordo=actual_date + datetime.timedelta(4))
    mommy.make('SistemaCultura', ente_federado__cod_ibge=113, data_publicacao_acordo=actual_date + datetime.timedelta(5))

    data_range_param = '?data_adesao_min={}&data_adesao_max={}'.format(old_date, actual_date)
    url = url_sistemadeculturalocal + data_range_param

    request = client.get(url, content_type="application/hal+json")

    data = request.data["_embedded"]["items"]

    assert len(data) == 2
    assert data[0]["data_adesao"] == str(actual_date)


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


def test_choices_situacao_acoes_plano_trabalho(client):
    request = client.options(url_acoesplanotrabalho)

    situacoes_list = []

    situacoes = SituacoesArquivoPlano.objects.all()

    for situacao in situacoes:
        situacoes_list.append(
            {'id': situacao.id, 'description': situacao.descricao}
            )

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


def test_retorno_sistemas_cultura_municipios(client):
    """ Testa retorno de sistema culturas que são referentes a adesões
    de entes federados municipais """

    municipio = mommy.make('SistemaCultura', ente_federado__cod_ibge=123456, ente_federado__nome="Municipio")
    estado = mommy.make('SistemaCultura', ente_federado__cod_ibge=11, ente_federado__nome="Estado")

    url = url_sistemadeculturalocal + '?municipal=true'

    response = client.get(url)
    municipio_response = response.data['_embedded']['items'][0]['_embedded']['ente_federado']['nome']

    assert len(response.data['_embedded']['items']) == 1
    assert municipio_response == municipio.ente_federado.nome


def test_retorno_sistemas_cultura_estados(client):
    """ Testa retorno de sistema culturas que são referentes a adesões
    de entes federados estaduais """

    municipio = mommy.make('SistemaCultura', ente_federado__cod_ibge=123456, ente_federado__nome="Municipio")
    estado = mommy.make('SistemaCultura', ente_federado__cod_ibge=11, ente_federado__nome="Estado")

    url = url_sistemadeculturalocal + '?estadual=true'

    response = client.get(url)
    estado_response = response.data['_embedded']['items'][0]['_embedded']['ente_federado']['nome']

    assert len(response.data['_embedded']['items']) == 1
    assert estado_response == estado.ente_federado.nome


def test_retorno_sistemas_cultura_estadual_vazio(client):
    """ Testa retorno dos sistemas cultura ao fornecer o parâmetro estadual vazio """

    municipio = mommy.make('SistemaCultura', ente_federado__cod_ibge=123456, ente_federado__nome="Municipio")
    estado = mommy.make('SistemaCultura', ente_federado__cod_ibge=11, ente_federado__nome="Estado")

    url = url_sistemadeculturalocal + '?estadual=&municipal=true'
    response = client.get(url)

    municipio_response = response.data['_embedded']['items'][0]['_embedded']['ente_federado']['nome']

    assert len(response.data['_embedded']['items']) == 1
    assert municipio_response == municipio.ente_federado.nome


def test_retorno_sistemas_cultura_municipal_vazio(client):
    """ Testa retorno dos sistemas cultura ao fornecer o parâmetro municipal vazio """

    municipio = mommy.make('SistemaCultura', ente_federado__cod_ibge=123456, ente_federado__nome="Municipio")
    estado = mommy.make('SistemaCultura', ente_federado__cod_ibge=11, ente_federado__nome="Estado")

    url = url_sistemadeculturalocal + '?estadual=true&municipal='
    response = client.get(url)

    estado_response = response.data['_embedded']['items'][0]['_embedded']['ente_federado']['nome']

    assert len(response.data['_embedded']['items']) == 1
    assert estado_response == estado.ente_federado.nome


def test_filtrar_por_nome_ente_federado_sigla_estado(client, sistema_cultura):
    """ Testa retorno de sistemas de cultura passando o nome do ente federado
    como parâmetro, nesse caso a sigla do estado"""

    url = url_sistemadeculturalocal + '?ente_federado=ba'

    response = client.get(url)

    assert len(response.data['_embedded']['items']) == 1
    assert response.data['_embedded']['items'][0]['_embedded']['ente_federado']['nome'] == sistema_cultura.ente_federado.nome


def test_filtrar_por_nome_ente_federado_nome(client, sistema_cultura):
    """ Testa retorno de sistemas de cultura passando o nome do ente federado
    como parâmetro"""

    url = url_sistemadeculturalocal + '?ente_federado={}'.format(sistema_cultura.ente_federado.nome)

    response = client.get(url)

    assert len(response.data['_embedded']['items']) == 1
    assert response.data['_embedded']['items'][0]['_embedded']['ente_federado']['nome'] == sistema_cultura.ente_federado.nome


def test_filtrar_por_nome_ente_federado_vazio(client, sistema_cultura):
    """ Testa retorno de sistemas de cultura ao passar o parâmetro vazio """

    SistemaCultura.objects.exclude(id=sistema_cultura.id).delete()

    url = url_sistemadeculturalocal + '?ente_federado='

    response = client.get(url)

    assert len(response.data['_embedded']['items']) == 1


def test_counts_com_estado_e_municipio(client):
    """ Testa as contagens em uma busca que retorna estados e municipios"""

    municipio = mommy.make('SistemaCultura', ente_federado__cod_ibge=123456, ente_federado__nome="Tocantins")
    estado = mommy.make('SistemaCultura', ente_federado__cod_ibge=11, ente_federado__nome="Tocantins")

    municipio_aderido = mommy.make('SistemaCultura', ente_federado__cod_ibge=123457, ente_federado__nome="Tocantins",
        estado_processo=6)
    estado_aderido = mommy.make('SistemaCultura', ente_federado__cod_ibge=12, ente_federado__nome="Tocantins",
        estado_processo=6)

    url = url_sistemadeculturalocal + '?ente_federado=Tocantins'

    response = client.get(url)
    count_municipios = response.data['municipios']
    count_estados = response.data['estados']
    count_municipios_aderidos = response.data['municipios_aderidos']
    count_estados_aderidos = response.data['estados_aderidos']

    assert count_municipios == 2
    assert count_estados == 2
    assert count_municipios_aderidos == 1
    assert count_estados_aderidos == 1


def test_counts_com_apenas_estados(client):
    """ Testa as contagens em uma busca que retorna somente estados"""

    municipio = mommy.make('SistemaCultura', ente_federado__cod_ibge=123456, ente_federado__nome="Tocantins")
    estado = mommy.make('SistemaCultura', ente_federado__cod_ibge=11, ente_federado__nome="Tocantins")

    municipio_aderido = mommy.make('SistemaCultura', ente_federado__cod_ibge=123457, ente_federado__nome="Tocantins",
        estado_processo=6)
    estado_aderido = mommy.make('SistemaCultura', ente_federado__cod_ibge=12, ente_federado__nome="Tocantins",
        estado_processo=6)


    url = url_sistemadeculturalocal + '?ente_federado=Tocantins&estadual=true'

    response = client.get(url)
    count_municipios = response.data['municipios']
    count_estados = response.data['estados']
    count_municipios_aderidos = response.data['municipios_aderidos']
    count_estados_aderidos = response.data['estados_aderidos']

    assert count_municipios == 0
    assert count_estados == 2
    assert count_municipios_aderidos == 0
    assert count_estados_aderidos == 1


def test_counts_com_apenas_municipios(client):
    """ Testa as contagens em uma busca que retorna um municipio não aderido"""

    municipio = mommy.make('SistemaCultura', ente_federado__cod_ibge=123456, ente_federado__nome="Tocantins")
    estado = mommy.make('SistemaCultura', ente_federado__cod_ibge=11, ente_federado__nome="Tocantins")

    municipio_aderido = mommy.make('SistemaCultura', ente_federado__cod_ibge=123457, ente_federado__nome="Tocantins",
        estado_processo=6)
    estado_aderido = mommy.make('SistemaCultura', ente_federado__cod_ibge=12, ente_federado__nome="Tocantins",
        estado_processo=6)

    url = url_sistemadeculturalocal + '?ente_federado=Tocantins&municipal=true'

    response = client.get(url)
    count_municipios = response.data['municipios']
    count_estados = response.data['estados']
    count_municipios_aderidos = response.data['municipios_aderidos']
    count_estados_aderidos = response.data['estados_aderidos']

    assert count_municipios == 2
    assert count_estados == 0
    assert count_municipios_aderidos == 1
    assert count_estados_aderidos == 0


def test_ordenar_resultados_da_api_de_forma_ascendente_por_nome_municipio(client):
    """ Testa a ordenação ascendente do resultado da API por cidade(nome_municipio) """

    SistemaCultura.objects.all().delete()

    nomes_entes = ['Brasilia', 'Zé Doca', 'Abaetetuba', 'Abaetetuba']

    for nome in nomes_entes:
        mommy.make('SistemaCultura',
                   ente_federado__nome=nome,
                   ente_federado__cod_ibge=random.randint(100, 900),
                   _fill_optional=True)

    url = url_sistemadeculturalocal + '?ordering=ente_federado__nome'
    response = client.get(url)

    entes = response.data['_embedded']['items']

    assert entes[0]['_embedded']['ente_federado']['nome'] == nomes_entes[2]
    assert entes[1]['_embedded']['ente_federado']['nome'] == nomes_entes[3]
    assert entes[2]['_embedded']['ente_federado']['nome'] == nomes_entes[0]
    assert entes[3]['_embedded']['ente_federado']['nome'] == nomes_entes[1]


def test_ordenar_resultados_da_api_de_forma_descendente_por_nome_municipio(client):
    """ Testa a ordenação descendente do resultado da API por cidade(nome_municipio) """

    SistemaCultura.objects.all().delete()

    nomes_entes = ['Brasilia', 'Zé Doca', 'Abaetetuba']

    for nome in nomes_entes:
        mommy.make('SistemaCultura',
                   ente_federado__nome=nome,
                   ente_federado__cod_ibge=random.randint(100, 900),
                   _fill_optional=True)

    url = url_sistemadeculturalocal + '?ordering=-ente_federado__nome'
    response = client.get(url)

    entes = response.data['_embedded']['items']

    assert entes[0]['_embedded']['ente_federado']['nome'] == nomes_entes[1]
    assert entes[1]['_embedded']['ente_federado']['nome'] == nomes_entes[0]
    assert entes[2]['_embedded']['ente_federado']['nome'] == nomes_entes[2]


@pytest.mark.parametrize("query,componente", [
    ("situacao_lei_sistema", "legislacao"),
    ("situacao_orgao_gestor", "orgao_gestor"),
    ("situacao_fundo_cultura", "fundo_cultura"),
    ("situacao_plano_cultura", "plano"),
    ("situacao_conselho_cultural", "conselho"),
    ])
def test_filtra_por_situacao_id_componente_sistema_de_cultura(client, query, componente):
    """ Testa retorno ao filtrar sistemas de cultura locais por id da situação
    dos componentes do plano de trabalho """

    SistemaCultura.objects.exclude(legislacao__situacao=None).delete()

    sistema_cultura = mommy.make("SistemaCultura", _fill_optional=['legislacao', 'orgao_gestor',
        'fundo_cultura', 'plano', 'conselho'])

    situacao = getattr(sistema_cultura, componente).situacao
    url = url_sistemadeculturalocal + '?{}={}'.format(query, situacao)

    response = client.get(url)

    assert len(response.data['_embedded']['items']) == 1


def test_filtra_componente_lei_por_multiplos_ids_situacao(client):
    """ Testa retorno ao filtrar sistemas de cultura locais por múltiplos ids da situação
    do componente lei sistema cultura """

    SistemaCultura.objects.filter(Q(legislacao__situacao=1) | Q(legislacao__situacao=0)).delete()

    situacoes = [0, 1, 5]
    sistemas = mommy.make(
        "SistemaCultura", ente_federado__cod_ibge=1234567, _fill_optional=['legislacao'], _quantity=3)
    for sistema, situacao in zip(sistemas, situacoes):
        sistema.legislacao.situacao = situacao
        sistema.legislacao.save()

    url = url_sistemadeculturalocal + '?situacao_lei_sistema=0&situacao_lei_sistema=1'

    response = client.get(url)

    assert len(response.data['_embedded']['items']) == 2

    for componentes in response.data['_embedded']['items']:
        situacao = componentes['acoes_plano_trabalho']['_embedded']['criacao_lei_sistema']['situacao']
        assert situacao == 'Avaliando anexo' or situacao == 'Em preenchimento'


def test_filtra_componente_conselho_por_multiplos_ids_situacao(client):
    """ Testa retorno ao filtrar sistemas de cultura locais por múltiplos ids da situação
    do componente conselho cultural do plano de trabalho """

    situacoes = [0, 1, 5]
    sistemas = mommy.make(
        "SistemaCultura", ente_federado__cod_ibge=1234567, _fill_optional='conselho', _quantity=3)
    for sistema, situacao in zip(sistemas, situacoes):
        sistema.conselho.situacao = situacao
        sistema.conselho.save()

    url = url_sistemadeculturalocal + '?situacao_conselho_cultural=0&situacao_conselho_cultural=1'

    response = client.get(url)

    assert len(response.data['_embedded']['items']) == 2

    for componentes in response.data['_embedded']['items']:
        situacao = componentes['acoes_plano_trabalho']['_embedded']['criacao_conselho_cultural']['situacao']
        assert situacao == 'Avaliando anexo' or situacao == 'Em preenchimento'


def test_filtra_componente_fundo_por_multiplos_ids_situacao(client):
    """ Testa retorno ao filtrar sistemas de cultura locais por múltiplos ids da situação
    do componente fundo cultura do plano de trabalho """

    situacoes = [0, 1, 5]
    sistemas = mommy.make(
        "SistemaCultura", ente_federado__cod_ibge=1234567, _fill_optional='fundo_cultura', _quantity=3)
    for sistema, situacao in zip(sistemas, situacoes):
        sistema.fundo_cultura.situacao = situacao
        sistema.fundo_cultura.save()

    url = url_sistemadeculturalocal + '?situacao_fundo_cultura=0&situacao_fundo_cultura=1'

    response = client.get(url)

    assert len(response.data['_embedded']['items']) == 2

    for componentes in response.data['_embedded']['items']:
        situacao = componentes['acoes_plano_trabalho']['_embedded']['criacao_fundo_cultura']['situacao']
        assert situacao == 'Avaliando anexo' or situacao == 'Em preenchimento'


def test_filtra_componente_orgao_por_multiplos_ids_situacao(client):
    """ Testa retorno ao filtrar sistemas de cultura locais por múltiplos ids da situação
    do componente órgão gestor do plano de trabalho """

    situacoes = [0, 1, 5]
    sistemas = mommy.make(
        "SistemaCultura", ente_federado__cod_ibge=1234567, _fill_optional='orgao_gestor', _quantity=3)
    for sistema, situacao in zip(sistemas, situacoes):
        sistema.orgao_gestor.situacao = situacao
        sistema.orgao_gestor.save()

    url = url_sistemadeculturalocal + '?situacao_orgao_gestor=0&situacao_orgao_gestor=1'

    response = client.get(url)

    assert len(response.data['_embedded']['items']) == 2

    for componentes in response.data['_embedded']['items']:
        situacao = componentes['acoes_plano_trabalho']['_embedded']['criacao_orgao_gestor']['situacao']
        assert situacao == 'Avaliando anexo' or situacao == 'Em preenchimento'


def test_filtra_componente_plano_por_multiplos_ids_situacao(client):
    """ Testa retorno ao filtrar sistemas de cultura locais por múltiplos ids da situação
    do componente plano cultura do plano de trabalho """

    situacoes = [0, 1, 5]
    sistemas = mommy.make(
        "SistemaCultura", ente_federado__cod_ibge=1234567, _fill_optional='plano', _quantity=3)
    for sistema, situacao in zip(sistemas, situacoes):
        sistema.plano.situacao = situacao
        sistema.plano.save()

    url = url_sistemadeculturalocal + '?situacao_plano_cultura=0&situacao_plano_cultura=1'

    response = client.get(url)

    assert len(response.data['_embedded']['items']) == 2

    for componentes in response.data['_embedded']['items']:
        situacao = componentes['acoes_plano_trabalho']['_embedded']['criacao_plano_cultura']['situacao']
        assert situacao == 'Avaliando anexo' or situacao == 'Em preenchimento'


def test_pesquisa_por_nome_ente_para_entes_com_acento_no_nome(client):
    ''' Pesquisa (sem acento) o nome de um ente que tenha acento - Deve retornar normalmente'''

    mommy.make('SistemaCultura', ente_federado__cod_ibge=123456, ente_federado__nome='Goiás')

    url = url_sistemadeculturalocal + '?ente_federado=Goias'

    request = client.get(url, content_type="application/hal+json")

    assert request.data["_embedded"]["items"][0]["_embedded"]["ente_federado"]["nome"] == 'Goiás'


@pytest.mark.parametrize("query, componente", [
    ("data_lei_min", "legislacao"),
    ("data_orgao_gestor_min", "orgao_gestor"),
    ("data_conselho_min", "conselho"),
    ("data_fundo_cultura_min", "fundo_cultura"),
    ("data_plano_min", "plano")
    ])
def test_filtra_por_data_min_componente_sistema_de_cultura(client, query, componente):
    """ Testa retorno ao filtrar sistemas de cultura por data de publicação mínima
    dos componentes do plano de trabalho """

    sistema_cultura = mommy.make("SistemaCultura", _fill_optional=['legislacao',
        'orgao_gestor', 'conselho', 'fundo_cultura', 'plano'])

    componente = getattr(sistema_cultura, componente)
    componente.data_publicacao = "2016-01-01"
    componente.save()

    url = url_sistemadeculturalocal + '?{}=1/1/2016'.format(query)

    response = client.get(url)

    assert len(response.data['_embedded']['items']) == 1


@pytest.mark.parametrize("query, componente", [
    ("data_lei_max", "legislacao"),
    ("data_orgao_gestor_max", "orgao_gestor"),
    ("data_conselho_max", "conselho"),
    ("data_fundo_cultura_max", "fundo_cultura"),
    ("data_plano_max", "plano")
    ])
def test_filtra_por_data_max_componente_sistema_de_cultura(client, query, componente):
    """ Testa retorno ao filtrar sistemas de cultura por data de publicação máxima
    dos componentes do plano de trabalho """

    sistema_cultura = mommy.make("SistemaCultura", _fill_optional=['legislacao',
        'orgao_gestor', 'conselho', 'fundo_cultura', 'plano'])

    componente = getattr(sistema_cultura, componente)
    componente.data_publicacao = "2016-01-01"
    componente.save()

    url = url_sistemadeculturalocal + '?{}=1/1/2019'.format(query)

    response = client.get(url)

    assert len(response.data['_embedded']['items']) == 1