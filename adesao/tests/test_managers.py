import pytest
from model_mommy import mommy

from adesao.models import SistemaCultura

def test_se_um_manager_retorna_apenas_as_ultimas_instancias_de_um_sistema_cultura(client, sistemacultura_10):
    """Testa se o SistemaManager retorna apenas a ultima instancia de todos os entes 
        federados que estão registrados"""

    sistemas = SistemaCultura.sistema.count()

    assert sistemas == 10


def test_filtrar_um_determinado_estado_usando_o_manager_sistema(client, sistemacultura_10):

    sistemas = SistemaCultura.sistema.filter(ente_federado__cod_ibge=11)

    assert sistemas.count() == 1


def test_get_or_create_usando_o_manager_sistema(client, sistemacultura_10):

    acre, acre_created = SistemaCultura.sistema.get_or_create(ente_federado__cod_ibge=11)
    sp, sp_created = SistemaCultura.sistema.get_or_create(ente_federado__cod_ibge=10)

    assert acre
    assert not acre_created

    assert sp
    assert sp_created



def test_retornar_todo_o_historico_de_um_ente_federado(client, sistemacultura_10):

    ente = SistemaCultura.historico.ente(cod_ibge=11)

    assert ente.count() == 2
