import pytest
import random

from rest_framework import status

from model_mommy import mommy

pytestmark = pytest.mark.django_db

url_sistemadeculturalocal = '/api/v1/sistemadeculturalocal/'
url_acoesplanotrabalho = '/api/v1/acoesplanotrabalho/'

def test_municipios_list_endpoint_returning_200_OK(client):

    request = client.get(url_sistemadeculturalocal)

    assert request.status_code == status.HTTP_200_OK


def test_URL_sistema_cultura_local_retorna_10_sistemas(client):

    sistemas = mommy.make('Municipio', _quantity=12)

    request = client.get(url_sistemadeculturalocal,
                         content_type="application/hal+json")

    assert isinstance(request.data["_embedded"]["items"], list)
    assert len(request.data["_embedded"]["items"]) == 10


def test_404_recupera_ID_sistema_cultura_local(client):

    url = url_sistemadeculturalocal + '45/'

    request = client.get(url,content_type="application/hal+json")

    assert request.status_code == status.HTTP_404_NOT_FOUND


def test_recupera_ID_param_sistema_cultura_local(client):

    municipio = mommy.make('Municipio')
    municipio_id = '{}/'.format(municipio.id)

    url = url_sistemadeculturalocal + municipio_id


    request = client.get(url, content_type="application/hal+json")

    assert request.status_code == status.HTTP_200_OK
    assert request.data["id"] == municipio.id


def test_entidades_principais_sistema_cultura_local(client):

    municipio = mommy.make('Municipio')
    municipio_id = '{}/'.format(municipio.id)

    url = url_sistemadeculturalocal + municipio_id

    request = client.get(url,content_type="application/hal+json")

    entidades = set(["governo","ente_federado", "conselho",
        "_embedded","situacao_adesao","_links","id"])

    assert entidades.symmetric_difference(request.data) == set()


def test_campos_do_objeto_governo_ao_retornar_sistema_cultura_local(client):

    municipio = mommy.make('Municipio')
    municipio_id = '{}/'.format(municipio.id)

    url = url_sistemadeculturalocal + municipio_id

    request = client.get(url, content_type="application/hal+json")

    campos = set(["nome_prefeito", "email_institucional_prefeito",
                  "termo_posse_prefeito"])

    assert campos.symmetric_difference(request.data["governo"]) == set()


def test_campos_do_objeto_ente_federado_ao_retornar_sistema_cultura_local(client):

    municipio = mommy.make('Municipio')
    municipio_id = '{}/'.format(municipio.id)

    url = url_sistemadeculturalocal + municipio_id

    request = client.get(url, content_type="application/hal+json")

    campos = set(["cnpj_prefeitura","endereco_eletronico","telefones","localizacao"])

    assert campos.symmetric_difference(request.data["ente_federado"]) == set()


def test_campos_do_objeto_embedded_ao_retornar_sistema_cultura_local(client):

    municipio = mommy.make('Municipio')
    municipio_id = '{}/'.format(municipio.id)

    url = url_sistemadeculturalocal + municipio_id

    request = client.get(url, content_type="application/hal+json")

    campos = set(["acoes_plano_trabalho"])

    assert campos.symmetric_difference(request.data["_embedded"]) == set()


def test_campos_do_objeto_conselho_ao_retornar_sistema_cultura_local(client):

    municipio = mommy.make('Municipio')
    conselho_cultural= mommy.make('ConselhoCultural')
    plano_trabalho = mommy.make('PlanoTrabalho',conselho_cultural=conselho_cultural)
    usuario = mommy.make('Usuario',municipio=municipio,plano_trabalho=plano_trabalho)
    conselheiro = mommy.make('Conselheiro',conselho=conselho_cultural)
    municipio_id = '{}/'.format(municipio.id)

    url = url_sistemadeculturalocal + municipio_id

    request = client.get(url, content_type="application/hal+json")

    campos = set(["conselheiros"])

    assert campos.symmetric_difference(request.data["conselho"]) == set()


def test_planotrabalho_list_endpoint_returning_200_OK(client):

    request = client.get(url_acoesplanotrabalho)

    assert request.status_code == status.HTTP_200_OK


def test_planotrabalho_list_retorna_lista_com_10(client):

    planos = mommy.make('PlanoTrabalho',13)

    request = client.get(url_acoesplanotrabalho,
            content_type="application/hal+json")

    assert isinstance(request.data["_embedded"]["items"], list) 
    assert len(request.data["_embedded"]["items"]) == 10


def test_acoesplanotrabalho_retorna_404_para_id_nao_valido(client):

    url = url_acoesplanotrabalho + '55/'

    request = client.get(url, content_type="application/hal+json")

    assert request.status_code == status.HTTP_404_NOT_FOUND


def test_acoesplanotrabalho_retorna_para_id_valido(client):

    plano_trabalho = mommy.make('PlanoTrabalho')
    plano_trabalho_id = '{}/'.format(plano_trabalho.id)

    url = url_acoesplanotrabalho + plano_trabalho_id

    request = client.get(url, content_type="application/hal+json")

    assert request.status_code == status.HTTP_200_OK
    assert request.data["id"] == plano_trabalho.id


def test_campos_acoesplanotrabalho(client):

    plano_trabalho = mommy.make('PlanoTrabalho')
    plano_trabalho_id = '{}/'.format(plano_trabalho.id)

    url = url_acoesplanotrabalho + plano_trabalho_id

    request = client.get(url, content_type="application/hal+json")

    campos = set(["criacao_lei_sistema_cultura","criacao_orgao_gestor",
        "criacao_plano_cultura","criacao_fundo_cultura","criacao_conselho_cultural",
        "_links","id","_embedded"])

    assert campos.symmetric_difference(request.data) == set()

def test_objeto_embedded_acoesplanotrabalho(client):

    plano_trabalho = mommy.make('PlanoTrabalho')
    plano_trabalho_id = '{}/'.format(plano_trabalho.id)

    url = url_acoesplanotrabalho + plano_trabalho_id

    request = client.get(url, content_type="application/hal+json")

    campos = set(["sistema_cultura_local"])

    assert campos.symmetric_difference(request.data["_embedded"]) == set()


def test_objeto_criacao_lei_sistema_cultura_acoesplanotrabalho(client):

    criacao_sistema = mommy.make('CriacaoSistema')
    plano_trabalho = mommy.make('PlanoTrabalho',criacao_sistema=criacao_sistema)
    plano_trabalho_id = '{}/'.format(plano_trabalho.id)

    url = url_acoesplanotrabalho + plano_trabalho_id

    request = client.get(url, content_type="application/hal+json")

    campos = set(["lei_sistema_cultura","situacao"])

    assert campos.symmetric_difference(request.data["criacao_lei_sistema_cultura"]) == set()


def test_objeto_criacao_orgao_gestor_acoesplanotrabalho(client):

    orgao_gestor = mommy.make('OrgaoGestor')
    plano_trabalho = mommy.make('PlanoTrabalho',orgao_gestor=orgao_gestor)
    plano_trabalho_id = '{}/'.format(plano_trabalho.id)

    url = url_acoesplanotrabalho + plano_trabalho_id

    request = client.get(url, content_type="application/hal+json")

    campos = set(["relatorio_atividade_secretaria","situacao"])

    assert campos.symmetric_difference(request.data["criacao_orgao_gestor"]) == set()


def test_objeto_criacao_plano_cultura_acoesplanotrabalho(client):

    plano_cultura= mommy.make('PlanoCultura')
    plano_trabalho = mommy.make('PlanoTrabalho',plano_cultura=plano_cultura)
    plano_trabalho_id = '{}/'.format(plano_trabalho.id)

    url = url_acoesplanotrabalho + plano_trabalho_id

    request = client.get(url, content_type="application/hal+json")

    campos = set(["relatorio_diretrizes_aprovadas","minuta_preparada",
        "ata_reuniao_aprovacao_plano","ata_votacao_projeto_lei",
        "lei_plano_cultura","situacao"])

    assert campos.symmetric_difference(request.data["criacao_plano_cultura"]) == set()


def test_objeto_criacao_fundo_cultura_acoesplanotrabalho(client):

    fundo_cultura = mommy.make('FundoCultura')
    plano_trabalho = mommy.make('PlanoTrabalho',fundo_cultura=fundo_cultura)
    plano_trabalho_id = '{}/'.format(plano_trabalho.id)

    url = url_acoesplanotrabalho + plano_trabalho_id

    request = client.get(url, content_type="application/hal+json")

    campos = set(["cnpj_fundo_cultura","lei_fundo_cultura","situacao"])

    assert campos.symmetric_difference(request.data["criacao_fundo_cultura"]) == set()


def test_objeto_criacao_conselho_cultural_acoesplanotrabalho(client):

    conselho_cultural = mommy.make('ConselhoCultural')
    plano_trabalho = mommy.make('PlanoTrabalho',conselho_cultural=conselho_cultural)
    plano_trabalho_id = '{}/'.format(plano_trabalho.id)

    url = url_acoesplanotrabalho + plano_trabalho_id

    request = client.get(url, content_type="application/hal+json")

    campos = set(["ata_regimento_aprovado","situacao"])

    assert campos.symmetric_difference(request.data["criacao_conselho_cultural"]) == set()


def test_retorno_maximo_de_100_objetos_sistema_de_cultura(client):

    municipio = mommy.make('Municipio',150)
    limit_param = '?limit=150'

    url = url_sistemadeculturalocal + limit_param

    request = client.get(url, content_type="application/hal+json")

    assert len(request.data["_embedded"]["items"]) == 100


def test_retorno_maximo_de_100_objetos_acoes_plano_trabalho(client):

    municipio = mommy.make('PlanoTrabalho',150)
    limit_param = '?limit=150'

    url = url_acoesplanotrabalho + limit_param

    request = client.get(url, content_type="application/hal+json")

    assert len(request.data["_embedded"]["items"]) == 100


def test_pesquisa_por_cnpj_prefeitura_em_sistema_de_cultura(client):

    municipio = mommy.make('Municipio',50)
    cnpj_param = '?cnpj_prefeitura={}'.format(municipio[0].cnpj_prefeitura)

    url = url_sistemadeculturalocal + cnpj_param

    request = client.get(url, content_type="application/hal+json")

    assert len(request.data["_embedded"]["items"]) == 1
    assert request.data["_embedded"]["items"][0]["ente_federado"]["cnpj_prefeitura"] == municipio[0].cnpj_prefeitura


def test_pesquisa_por_nome_municipio_em_sistema_de_cultura(client):

    cidades = mommy.make('Cidade',50)

    for cidade in cidades:
         mommy.make('Municipio',cidade=cidade)

    nome_municipio_param = '?nome_municipio={}'.format(cidades[0].nome_municipio)

    url = url_sistemadeculturalocal + nome_municipio_param

    request = client.get(url, content_type="application/hal+json")

    assert len(request.data["_embedded"]["items"]) == 1
    assert request.data["_embedded"]["items"][0]["ente_federado"]["localizacao"]["cidade"]["nome_municipio"] == cidades[0].nome_municipio


def test_pesquisa_por_estado_sigla_em_sistema_de_cultura(client):

    municipios = mommy.make('Municipio',50)

    estado_sigla_param = '?estado_sigla={}'.format(municipios[0].estado.sigla)

    url = url_sistemadeculturalocal + estado_sigla_param

    request = client.get(url, content_type="application/hal+json")

    for municipio in request.data["_embedded"]["items"]:
        assert municipio["ente_federado"]["localizacao"]["estado"]["sigla"] == municipios[0].estado.sigla


def test_pesquisa_por_situacao_adesao_1_em_sistema_de_cultura(client):

    municipios = mommy.make('Municipio',50)
    estados_processo = ['1','2','3','4','5','6']

    for municipio in municipios:
        mommy.make('Usuario', municipio=municipio,
                estado_processo=random.choice(estados_processo))

    situacao_adesao_param = '?situacao_adesao=1'

    url = url_sistemadeculturalocal + situacao_adesao_param

    request = client.get(url, content_type="application/hal+json")

    for municipio in request.data["_embedded"]["items"]:
        assert municipio["situacao_adesao"]["situacao_adesao"] == 'Aguardando envio da documentação' 


def test_pesquisa_por_situacao_adesao_2_em_sistema_de_cultura(client):

    municipios = mommy.make('Municipio',50)
    estados_processo = ['1','2','3','4','5','6']

    for municipio in municipios:
        mommy.make('Usuario', municipio=municipio,
                estado_processo=random.choice(estados_processo))

    situacao_adesao_param = '?situacao_adesao=2'

    url = url_sistemadeculturalocal + situacao_adesao_param

    request = client.get(url, content_type="application/hal+json")

    for municipio in request.data["_embedded"]["items"]:
        assert municipio["situacao_adesao"]["situacao_adesao"] == 'Documentação Recebida - Aguarda Análise' 


def test_pesquisa_por_situacao_adesao_3_em_sistema_de_cultura(client):

    municipios = mommy.make('Municipio',50)
    estados_processo = ['1','2','3','4','5','6']

    for municipio in municipios:
        mommy.make('Usuario', municipio=municipio,
                estado_processo=random.choice(estados_processo))

    situacao_adesao_param = '?situacao_adesao=3'

    url = url_sistemadeculturalocal + situacao_adesao_param

    request = client.get(url, content_type="application/hal+json")

    for municipio in request.data["_embedded"]["items"]:
        assert municipio["situacao_adesao"]["situacao_adesao"] == 'Diligência Documental' 


def test_pesquisa_por_situacao_adesao_4_em_sistema_de_cultura(client):

    municipios = mommy.make('Municipio',50)
    estados_processo = ['1','2','3','4','5','6']

    for municipio in municipios:
        mommy.make('Usuario', municipio=municipio,
                estado_processo=random.choice(estados_processo))

    situacao_adesao_param = '?situacao_adesao=4'

    url = url_sistemadeculturalocal + situacao_adesao_param

    request = client.get(url, content_type="application/hal+json")

    for municipio in request.data["_embedded"]["items"]:
        assert municipio["situacao_adesao"]["situacao_adesao"] == 'Encaminhado para assinatura do Secretário SAI' 


def test_pesquisa_por_situacao_adesao_5_em_sistema_de_cultura(client):

    municipios = mommy.make('Municipio',50)
    estados_processo = ['1','2','3','4','5','6']

    for municipio in municipios:
        mommy.make('Usuario', municipio=municipio,
                estado_processo=random.choice(estados_processo))

    situacao_adesao_param = '?situacao_adesao=5'

    url = url_sistemadeculturalocal + situacao_adesao_param

    request = client.get(url, content_type="application/hal+json")

    for municipio in request.data["_embedded"]["items"]:
        assert municipio["situacao_adesao"]["situacao_adesao"] == 'Aguarda Publicação no DOU' 


def test_pesquisa_por_situacao_adesao_6_em_sistema_de_cultura(client):

    municipios = mommy.make('Municipio',50)
    estados_processo = ['1','2','3','4','5','6']

    for municipio in municipios:
        mommy.make('Usuario', municipio=municipio,
                estado_processo=random.choice(estados_processo))

    situacao_adesao_param = '?situacao_adesao=6'

    url = url_sistemadeculturalocal + situacao_adesao_param

    request = client.get(url, content_type="application/hal+json")

    for municipio in request.data["_embedded"]["items"]:
        assert municipio["situacao_adesao"]["situacao_adesao"] == 'Publicado no DOU' 
