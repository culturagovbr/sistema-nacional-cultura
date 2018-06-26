import pytest

from model_mommy import mommy

from adesao.models import SistemaCultura
from adesao.models import Usuario
from adesao.models import Municipio
from adesao.models import Secretario
from adesao.models import Responsavel
from planotrabalho.models import PlanoTrabalho


@pytest.mark.xfail
def test_existe_um_model_SistemaCultura():

    with pytest.raises(ImportError):
        from adesao.models import SistemaCultura


def test_atributo_cadastrador_de_um_SistemaCultura():

    sistema = SistemaCultura()

    assert sistema._meta.get_field('cadastrador')


def test_atributo_cidade_de_um_SistemaCultura():

    sistema = SistemaCultura()

    assert sistema._meta.get_field('cidade')


def test_atributo_uf_de_um_SistemaCultura():

    sistema = SistemaCultura()

    assert sistema._meta.get_field('uf')


def test_SistemaCultura_save_cria_nova_instancia():
    """
    SistemaCultura deve sempre retornar uma nova instancia quando da tentativa
    de salvar os dados de uma instancia existente.
    """

    sistema = mommy.make('SistemaCultura')
    user = mommy.make('Usuario')

    sistema.cadastrador = user
    sistema.save()

    assert SistemaCultura.objects.count() == 2

    user.delete()
    [sistema.delete() for sistema in SistemaCultura.objects.all()]


def test_alterar_cadastrador_SistemaCultura(plano_trabalho):
    """ Testa método alterar_cadastrador da model SistemaCultura"""

    cadastrador_atual = Usuario.objects.first()
    uf = cadastrador_atual.municipio.estado
    user = mommy.make('Usuario')

    sistema = SistemaCultura(uf=uf, cadastrador=user)
    sistema.alterar_cadastrador()
    user.refresh_from_db()

    assert SistemaCultura.objects.all().count() == 1
    assert Municipio.objects.first().usuario == user
    assert PlanoTrabalho.objects.first().usuario == user
    assert Secretario.objects.first().usuario == user
    assert Responsavel.objects.first().usuario == user
    assert sistema.cadastrador.data_publicacao_acordo ==\
        cadastrador_atual.data_publicacao_acordo
    assert sistema.cadastrador.estado_processo == cadastrador_atual.estado_processo

    sistema.delete()
    user.delete()


def test_limpa_cadastrador_alterado_SistemaCultura(plano_trabalho):
    """ Testa método para limpar referências de um cadastrador para os outos
    componentes do sistema de adesão """

    cadastrador = Usuario.objects.first()
    sistema = SistemaCultura()
    sistema.limpa_cadastrador_alterado(cadastrador)

    cadastrador.refresh_from_db()

    assert cadastrador.plano_trabalho is None
    assert cadastrador.municipio is None
    assert cadastrador.secretario is None
    assert cadastrador.responsavel is None
    assert cadastrador.user.is_active is False

