import pytest

from rest_framework import status

pytestmark = pytest.mark.django_db

def test_municipios_list_endpoint_returning_200_OK(client):

    url = '/v1/sistemadeculturalocal/'
    host_request = 'api'

    request = client.get(url, HTTP_HOST=host_request)

    assert request.status_code == status.HTTP_200_OK
