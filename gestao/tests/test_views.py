import pytest

from django.core.urlresolvers import resolve
from model_mommy import mommy

from gestao.views import diligencia_view
from gestao.forms import DiligenciaForm

from gestao.models import Diligencia
from adesao.models import Municipio

pytestmark = pytest.mark.django_db

@pytest.fixture
def plano_trabalho():
    plano_trabalho = mommy.make("PlanoTrabalho")
    return plano_trabalho


@pytest.fixture
def url():
    """Retorna uma string contendo a URL preparada para ser formatada."""

    return "/gestao/{id}/diligencia/{componente}"

def test_url_diligencia_retorna_200(url, client, plano_trabalho):
    """Testa se há url referente à página de diligências. 
        A url teria o formato: gestao/id_plano_trabalho/diligencia/componente_plano_trabalho"""

    request = client.get(url.format(id=plano_trabalho.id, componente='plano_cultura'))
    
    assert request.status_code == 200


def test_resolve_url_atraves_sua_view_name(url, client, plano_trabalho):
    """Testa se o Django retorna a url através da sua view_name"""

    resolved = resolve(url.format(id=plano_trabalho.id, componente='plano_cultura'))

    assert resolved.url_name == "diligencia_componente"
    assert resolved.kwargs['pk'] == str(plano_trabalho.id)


def test_recepcao_componente_na_url_diligencia(url, client, plano_trabalho):
    """Testa se a url esta recebendo o componente correspondente a diligencia que sera escrita"""

    resolved = resolve(url.format(id=plano_trabalho.id, componente="lei_sistema"))

    assert resolved.kwargs["componente"] == "lei_sistema"


def test_url_componente_retorna_200(url, client, plano_trabalho):
    """Testa se a url retorna 200 ao acessar um componente"""

    request = client.get(url.format(id=plano_trabalho.id, componente="fundo_cultura"))

    assert request.status_code == 200


def test_url_retorna_404_caso_componente_nao_exista(url, client, plano_trabalho):
    """Testa se a URL retorna 404 caso o componente não exista"""
    
    request = client.get(url.format(id=plano_trabalho.id, componente="um_componente_qualquer"))

    assert request.status_code == 404

def test_renderiza_template(url, client, plano_trabalho):
    """ Testa se o método da view renderiza um template"""

    request = client.get(url.format(id=plano_trabalho.id, componente="lei_sistema_cultura"))
    assert request.content
    

def test_renderiza_template_diligencia(url, client, plano_trabalho):
    """Testa se o template específico da diligência é renderizado corretamente"""

    request = client.get(url.format(id=plano_trabalho.id, componente="conselho_cultural"))
    assert "gestao/diligencia/diligencia.html" == request.templates[0].name


def test_existencia_do_contexto_view(url, client, plano_trabalho):
    """Testa se o contexto existe no retorno da view """
    
    contexts = [
        'ente_federado',
        'nome_arquivo',
        'data_envio',
        'classificacoes',
        'historico_diligencias',
    ]

    request = client.get(url.format(id=plano_trabalho.id, componente="conselho_cultural"))

    for context in contexts:
        assert context in request.context



def test_valor_context_retornado_na_view(url, client, plano_trabalho):
    """Testa se há informações retornadas na view"""
    
    request = client.get(url.format(id=plano_trabalho.id, componente="fundo_cultura"))

    contexts = [
        'ente_federado',
        'nome_arquivo',
        'data_envio',
        'classificacoes',
        'historico_diligencias',
    ]

    for context in contexts:
        assert request.context[context] != ''


def test_retorno_post_criacao_diligencia(url, client, plano_trabalho):
    """Testa se retorna o status 201 na criação da diligência"""

    request = client.post(url.format(id=plano_trabalho.id, componente="fundo_cultura"), data={'texto_diligencia': 'bla', 'classificacao_arquivo': 'arquivo_incorreto'})

    assert request.status_code == 201


def test_retorno_400_post_criacao_diligencia(url, client, plano_trabalho):
    """ Testa se o status do retorno é 400 para requests sem os parâmetros esperados """

    request = client.post(url.format(id=plano_trabalho.id, componente="orgao_gestor"), data={'bla': ''})

    assert request.status_code == 400


def test_retorna_400_POST_classificacao_inexistente(url, rf, plano_trabalho):
    """
    Testa se o status do retorno é 400 quando feito um POST com a classificao invalida
    de um arquivo.
    """
    request = rf.post(url.format(id=plano_trabalho.id, componente="orgao_gestor"), data={'classificacao_arquivo': ''})

    response = diligencia_view(request, plano_trabalho.id, "orgao_gestor")

    assert response.status_code == 400


def test_form_diligencia_utlizado_na_diligencia_view(url, client, plano_trabalho):
    """Testa que existe um form no context da diligência view """

    request = client.get(url.format(id=plano_trabalho.id, componente="orgao_gestor"))

    assert request.context['form']


def test_tipo_do_form_utilizado_na_diligencia_view(url, client, plano_trabalho):
    """ Testa se o form utilizado na diligencia_view é do tipo DiligenciaForm """

    request = client.get(url.format(id=plano_trabalho.id, componente="orgao_gestor"))

    assert isinstance(request.context['form'], DiligenciaForm)


def test_invalido_form_para_post_diligencia(url, client, plano_trabalho):
    """ Testa se o form invalida post com dados errados """

    request = client.post(url.format(id=plano_trabalho.id, componente="orgao_gestor"), data={"classificacao_arquivo": "bla", "texto_diligencia": ''})

    assert request.status_code == 400


def test_valido_form_post_diligencia(url, client, plano_trabalho):
    """ Testa se o form valida post com dados corretos """

    request = client.post(url.format(id=plano_trabalho.id, componente="orgao_gestor"), data={"classificacao_arquivo": "arquivo_incorreto", "texto_diligencia": 'Ta errado cara'})

    assert request.status_code == 201


def test_obj_ente_federado(url, client, plano_trabalho):
    """ Testa se o objeto retornado ente_federado é uma instancia da model Municipio"""
        
    request = client.get(url.format(id=plano_trabalho.id, componente='orgao_gestor'))

    assert isinstance(request.context['ente_federado'], Municipio)


def test_404_para_plano_trabalho_invalido_diligencia(url, client):
    """ Testa se a view da diligência retorna 404 para um plano de trabalho inválido """

    request = client.get(url.format(id='7', componente='orgao_gestor'))

    assert request.status_code == 404
