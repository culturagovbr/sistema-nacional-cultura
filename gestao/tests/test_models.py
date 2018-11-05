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


@pytest.fixture(scope='function')
def diligencia():

    diligencia = mommy.make('Diligencia')

    yield

    diligencia.delete()


@pytest.fixture
def sistema(plano_trabalho):

    return PlanoTrabalho.objects.first()


def test_existencia_campos_atributo_models():
    """Testa se os atributos da model Diligencia existem"""

    diligencia = Diligencia()
    fields = ('id', 'texto_diligencia', 'classificacao_arquivo',
              'componente', 'data_criacao', 'usuario')
    for field in fields:
        assert diligencia._meta.get_field(field)


def test_campo_data_criacao_diligencia(diligencia):
    """
    Testa se o campo data_criacao presente na model Diligencia está sendo
    iniciado corretamente
    """

    diligencia = Diligencia.objects.first()

    assert diligencia.data_criacao == datetime.date.today()


def test_relacionamento_com_lei_sistema_diligencia_model(diligencia, sistema):
    """
    Testa relacionamento com o componente lei sistema do plano de trabalho na
    model Diligencia
    """

    sistema = sistema.criacao_sistema
    diligencia = Diligencia.objects.first()

    sistema.diligencias.add(diligencia)

    assert isinstance(diligencia.componente, CriacaoSistema)


def test_relacionamento_com_conselho_diligencia_model(diligencia, sistema):
    """
    Testa relacionamento com o componente conselho cultural do plano de
    trabalho na model Diligencia
    """

    sistema = sistema.conselho_cultural
    diligencia = Diligencia.objects.first()

    sistema.diligencias.add(diligencia)

    assert isinstance(diligencia.componente, ConselhoCultural)


def test_relacionamento_com_orgao_diligencia_model(diligencia, sistema):
    """
    Testa relacionamento com o componente orgão gestor do plano de trabalho
    na model Diligencia
    """

    sistema = sistema.orgao_gestor
    diligencia = Diligencia.objects.first()

    sistema.diligencias.add(diligencia)

    assert isinstance(diligencia.componente, OrgaoGestor)


def test_relacionamento_com_fundo_diligencia_model(diligencia, sistema):
    """
    Testa relacionamento com o componente fundo cultura do plano de trabalho
    na model Diligencia
    """

    sistema = sistema.fundo_cultura
    diligencia = Diligencia.objects.first()

    sistema.diligencias.add(diligencia)

    assert isinstance(diligencia.componente, FundoCultura)


def test_relacionamento_com_plano_diligencia_model(diligencia, sistema):
    """
    Testa relacionamento com o componente plano cultura do plano de trabalho na
    model Diligencia
    """

    sistema = sistema.plano_cultura
    diligencia = Diligencia.objects.first()

    sistema.diligencias.add(diligencia)

    assert isinstance(diligencia.componente, PlanoCultura)


@pytest.mark.skip()
def test_tipo_campo_sistema_cultura_model_diligencia(diligencia):
    """ Testa tipo do campo sistema_cultura na model Diligencia """

    diligencia = Diligencia()
    sistema_field = diligencia._meta.get_field('sistema_cultura')

    assert isinstance(sistema_field, ForeignKey)


@pytest.mark.skip()
def test_informacoes_sistema_cultura_na_diligencia():
    """
    Testa as informacoes do sistema_cultura na model de diligência
    """

    diligencia = mommy.make('DiligenciaSimples')
    sistema_cultura = mommy.make('SistemaCultura', diligencia=diligencia)

    assert isinstance(diligencia.sistema_cultura, ManyRelatedManager)