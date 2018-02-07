import pytest

from django.core.urlresolvers import resolve
from model_mommy import mommy

pytestmark = pytest.mark.django_db


@pytest.fixture
def url():
    """Retorna uma string contendo a URL preparada para ser formatada."""

    return "/gestao/{id}/diligencia/{componente}"

def test_url_diligencia_retorna_200(url, client):
    """Testa se há url referente à página de diligências. 
        A url teria o formato: gestao/id_plano_trabalho/diligencia/componente_plano_trabalho"""

    plano_trabalho = mommy.make("PlanoTrabalho")

    request = client.get(url.format(id=plano_trabalho.id, componente='plano_cultura'))
    
    assert request.status_code == 200


def test_resolve_url_atraves_sua_view_name(url, client):
    """Testa se o Django retorna a url através da sua view_name"""

    resolved = resolve(url.format(id='1', componente='plano_cultura'))

    assert resolved.url_name == "diligencia_componente"
    assert resolved.kwargs["pk"] == "1"


def test_recepcao_componente_na_url_diligencia(url, client):
    """Testa se a url esta recebendo o componente correspondente a diligencia que sera escrita"""

    resolved = resolve(url.format(id="1", componente="lei_sistema"))

    assert resolved.kwargs["componente"] == "lei_sistema"


def test_url_componente_retorna_200(url, client):
    """Testa se a url retorna 200 ao acessar um componente"""

    request = client.get(url.format(id="2", componente="fundo_cultura"))

    assert request.status_code == 200


def test_url_retorna_404_caso_componente_nao_exista(url, client):
    """Testa se a URL retorna 404 caso o componente não exista"""
    
    request = client.get(url.format(id=1, componente="um_componente_qualquer"))

    assert request.status_code == 404

def test_renderiza_template(url, client):
    """ Testa se o método da view renderiza um template"""

    request = client.get(url.format(id=1, componente="lei_sistema_cultura"))
    assert request.content
    

def test_renderiza_template_diligencia(url, client):
    """Testa se o template específico da diligência é renderizado corretamente"""

    request = client.get(url.format(id=1, componente="conselho_cultural"))

    assert "gestao/diligencia/diligencia.html" == request.templates[0].name


def test_existencia_do_contexto_view(url, client):
    """Testa se o contexto existe no retorno da view """
    
    contexts = [
        'ente_federado',
        'nome_arquivo',
        'data_envio',
        'classificacoes',
        'historico_diligencias',
    ]

    request = client.get(url.format(id=1, componente="conselho_cultural"))

    for context in contexts:
        assert context in request.context



def test_valor_context_retornado_na_view(url, client):
    """Testa se há informações retornadas na view"""
    
    request = client.get(url.format(id=1, componente="fundo_cultura"))

    contexts = [
        'ente_federado',
        'nome_arquivo',
        'data_envio',
        'classificacoes',
        'historico_diligencias',
    ]

    for context in contexts:
        assert request.context[context] != ''


def test_retorno_post_criacao_diligencia(url, client):
    """Testa se retorna o status 201 na criação da diligência"""

    request = client.post(url.format(id="2", componente="fundo_cultura"), data={'texto_diligencia':''})

    assert request.status_code == 201


def test_envio_de_dados_atraves_do_POST(url, client):
    """Testa se dados estão sendo enviados através do POST"""

    request = client.post(url.format(id=1, componente="fundo_cultura"), data={'texto_diligencia': 'Um corpo top da diligencia'})

    assert 'Um corpo top da diligencia' in request.content.decode()