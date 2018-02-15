import pytest

from gestao.models import Diligencia
from planotrabalho.models import (CriacaoSistema, OrgaoGestor, 
                                  ConselhoCultural, FundoCultura, PlanoCultura)

from model_mommy import mommy

pytestmark = pytest.mark.django_db


def test_existencia_campos_atributo_models():
    """Testa se os atributos da model Diligencia existem"""
    
    diligencia = Diligencia()
    fields = ('id', 'texto_diligencia', 'classificacao_arquivo', 
              'ente_federado', 'componente')
    for field in fields:
        assert diligencia._meta.get_field(field)


def test_relacionamento_com_lei_sistema_diligencia_model():
    """
        Testa relacionamento com o componente lei sistema do plano de trabalho na model Diligencia
    """

    sistema = mommy.make('CriacaoSistema')
    diligencia = mommy.make('Diligencia')
    
    sistema.diligencias.add(diligencia)

    assert isinstance(diligencia.componente, CriacaoSistema)


def test_relacionamento_com_conselho_diligencia_model():
    """
        Testa relacionamento com o componente conselho cultural do plano de trabalho na model Diligencia
    """

    sistema = mommy.make('ConselhoCultural')
    diligencia = mommy.make('Diligencia')
    
    sistema.diligencias.add(diligencia)

    assert isinstance(diligencia.componente, ConselhoCultural)


def test_relacionamento_com_orgao_diligencia_model():
    """
        Testa relacionamento com o componente orgão gestor do plano de trabalho na model Diligencia
    """

    sistema = mommy.make('OrgaoGestor')
    diligencia = mommy.make('Diligencia')
    
    sistema.diligencias.add(diligencia)

    assert isinstance(diligencia.componente, OrgaoGestor)


def test_relacionamento_com_fundo_diligencia_model():
    """
        Testa relacionamento com o componente fundo cultura do plano de trabalho na model Diligencia
    """

    sistema = mommy.make('FundoCultura')
    diligencia = mommy.make('Diligencia')
    
    sistema.diligencias.add(diligencia)

    assert isinstance(diligencia.componente, FundoCultura)


def test_relacionamento_com_plano_diligencia_model():
    """
        Testa relacionamento com o componente plano cultura do plano de trabalho na model Diligencia
    """

    sistema = mommy.make('PlanoCultura')
    diligencia = mommy.make('Diligencia')
    
    sistema.diligencias.add(diligencia)

    assert isinstance(diligencia.componente, PlanoCultura)