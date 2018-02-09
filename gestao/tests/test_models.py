import pytest

from gestao.models import Diligencia

pytestmark = pytest.mark.django_db


def test_existencia_campos_atributo_models():
    """Testa se os atributos da model Diligencia existem"""
    
    diligencia = Diligencia()
    fields = ('id', 'texto_diligencia', 'classificacao_arquivo', 
              'ente_federado', 'componente')
    for field in fields:
        assert diligencia._meta.get_field(field)