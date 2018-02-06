import pytest

from django.core.urlresolvers import resolve
from model_mommy import mommy

pytestmark = pytest.mark.django_db


def test_url_diligencia_retorna_200(client):
    """Testa se há url referente à página de diligências. 
        A url teria o formato: gestao/id_plano_trabalho/diligencia/componente_plano_trabalho"""

    plano_trabalho = mommy.make("PlanoTrabalho")

    request = client.get("/gestao/{}/diligencia/plano_cultura".format(plano_trabalho.id))
    
    assert request.status_code == 200


def test_resolve_url_atraves_sua_view_name(client):
    """Testa se o Django retorna a url através da sua view_name"""
    
    url = "/gestao/1/diligencia/plano_cultura"

    resolved = resolve(url)

    assert resolved.url_name == "diligencia_componente"
    assert resolved.kwargs["pk"] == "1"


def test_recepcao_componente_na_url_diligencia(client):
    """Testa se a url esta recebendo o componente correspondente a diligencia que sera escrita"""

    url = "/gestao/1/diligencia/lei_sistema"
    resolved = resolve(url)

    assert resolved.kwargs["componente"] == "lei_sistema"


def test_url_componente_retorna_200(client):
    """Testa se a url retorna 200 ao acessar um componente"""

    url = "/gestao/2/diligencia/fundo_cultura"

    request = client.get(url)

    assert request.status_code == 200
