import pytest

from model_mommy import mommy

from adesao.models import EnteFederado
from adesao.models import SistemaCultura


@pytest.fixture
def sistemacultura_10(django_db_setup, django_db_blocker):
    """
    Cria 10 diferentes entes de SistemaCultura
    """

    ufs_entes_federados = {
            11: "Acre",
            12: "Alagoas",
            13: "Amapá",
            14: "Bahia",
            15: "Ceará",
            16: "Distrito_Federal",
            17: "Espirito Santo",
            18: "Goias",
            19: "Maranhão",
            20: "Minas Gerais",
    }

    for cod_ibge, nome in ufs_entes_federados.items():
        mommy.make('EnteFederado', cod_ibge=cod_ibge, nome=nome)

    entes = EnteFederado.objects.all()

    for ente in entes:
        mommy.make('SistemaCultura', ente_federado=ente)

    sistemacultura_10 = SistemaCultura.objects.all()

    for sistema in sistemacultura_10:
        sistema.processo_sei = 1
        sistema.save()

    yield sistemacultura_10

    entes.delete()
    sistemacultura_10.delete()
