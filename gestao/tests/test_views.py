import pytest

from django.core.urlresolvers import resolve
from model_mommy import mommy

pytestmark = pytest.mark.django_db


def test_url_diligencia_retorna_200(client):
    """Testa se há url referente à página de diligências. 
        A url teria o formato: gestao/id_plano_trabalho/diligencia/componente_plano_trabalho"""

    plano_cultura = mommy.make("PlanoCultura")

    plano_trabalho = mommy.make("PlanoTrabalho", plano_cultura=plano_cultura)

    request = client.get("/gestao/{}/diligencia/plano_cultura".format(plano_trabalho.id))
    
    assert request.status_code == 200


def test_resolve_url_atraves_sua_view_name(client):
    """Testa se o Django retorna a url através da sua view_name"""
    
    url = "/gestao/1/diligencia/plano_cultura"

    resolved = resolve(url)

    assert resolved.url_name == "diligencia_componente"
    assert resolved.kwargs["pk"] == "1"