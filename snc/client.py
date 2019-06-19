import requests
from requests.auth import HTTPBasicAuth
from snc import settings
from adesao.utils import limpar_mascara
from json.decoder import JSONDecodeError

class Client():

    def consulta_cnpj(self, cnpj):
        cnpj = limpar_mascara(cnpj)
        response = requests.get(settings.RECEITA_URL + cnpj, 
            auth=HTTPBasicAuth(settings.RECEITA_USER, settings.RECEITA_PASSWORD))

        try:
            response = response.json()
            if response.get('erro', None):
                response = None

        except JSONDecodeError:
            response = None

        return response
