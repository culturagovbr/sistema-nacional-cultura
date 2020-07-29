import requests
from requests.auth import HTTPBasicAuth
from snc import settings
from adesao.utils import limpar_mascara
from json.decoder import JSONDecodeError

class Client():
    def consulta_cnpj(self, cnpj):
        infoconv_url = 'http://infoconv.turismo.gov.br/infoconv-proxy/api/cnpj/perfil3?listaCNPJ='
        cnpj = limpar_mascara(cnpj)
        response = requests.get(infoconv_url + cnpj)

        try:
            jsonResponse = response.json()

            if 'error' in jsonResponse:
                jsonResponse = None
            else:
                jsonResponse = jsonResponse[0]['cnpj']

        except JSONDecodeError:
            jsonResponse = None

        return jsonResponse
