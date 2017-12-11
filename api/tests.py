import pytest

from rest_framework import status

from model_mommy import mommy 

pytestmark = pytest.mark.django_db

def test_municipios_list_endpoint_returning_200_OK(client):

    url = '/v1/sistemadeculturalocal/'
    host_request = 'api'

    request = client.get(url, HTTP_HOST=host_request)

    assert request.status_code == status.HTTP_200_OK


def test_URL_sistema_cultura_local_retorna_10_sistemas(client):

    url = '/v1/sistemadeculturalocal/'
    host_request = 'api'

    sistemas = mommy.make('Municipio', _quantity=12)

    request = client.get(url, HTTP_HOST=host_request,
                         content_type="application/hal+json")

    assert isinstance(request.data["_embedded"]["items"], list)
    assert len(request.data["_embedded"]["items"]) == 10


def test_404_recupera_ID_sistema_cultura_local(client):

    url = '/v1/sistemadeculturalocal/45/'
    host_request = 'api'

    request = client.get(url, HTTP_HOST=host_request,
                        content_type="application/hal+json")

    assert request.status_code == status.HTTP_404_NOT_FOUND


def test_recupera_ID_param_sistema_cultura_local(client):

    municipio = mommy.make('Municipio')

    url = '/v1/sistemadeculturalocal/{}/'.format(municipio.id)
    host_request = 'api'


    request = client.get(url, HTTP_HOST=host_request,
                        content_type="application/hal+json")

    assert request.status_code == status.HTTP_200_OK
    assert request.data["id"] == municipio.id
    # __import__('ipdb').set_trace()


def test_entidades_principais_sistema_cultura_local(client):

    municipio = mommy.make('Municipio')

    url = '/v1/sistemadeculturalocal/{}/'.format(municipio.id)
    host_request = 'api'

    request = client.get(url, HTTP_HOST=host_request, content_type="application/hal+json")

    entidades = ["governo","ente_federado", "conselho", "_embedded"]

    for entidade in entidades:
        assert entidade in request.data
     
