import pytest
import datetime
from django.db.models import ForeignKey

from adesao.models import Municipio
from adesao.models import SistemaCultura
from gestao.models import Diligencia

from planotrabalho.models import PlanoTrabalho
from planotrabalho.models import CriacaoSistema
from planotrabalho.models import OrgaoGestor
from planotrabalho.models import ConselhoCultural
from planotrabalho.models import FundoCultura
from planotrabalho.models import PlanoCultura

from model_mommy import mommy

pytestmark = pytest.mark.django_db


def test_existencia_campos_atributo_models():
    """Testa se os atributos da model Diligencia existem"""

    diligencia = Diligencia()
    fields = ('id', 'texto_diligencia', 'classificacao_arquivo',
              'componente', 'data_criacao', 'usuario')
    for field in fields:
        assert diligencia._meta.get_field(field)

