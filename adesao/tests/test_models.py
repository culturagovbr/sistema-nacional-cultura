import pytest
from datetime import datetime

from django.utils import timezone
from model_mommy import mommy

from adesao.models import SistemaCultura
from adesao.models import Municipio
from adesao.models import Secretario
from adesao.models import Responsavel
from adesao.models import Funcionario
from adesao.models import Sede
from adesao.models import Gestor

from planotrabalho.models import PlanoTrabalho


@pytest.mark.xfail
def test_existe_um_model_SistemaCultura():

    with pytest.raises(ImportError):
        from adesao.models import SistemaCultura


def test_atributo_cadastrador_de_um_SistemaCultura():

    sistema = SistemaCultura()

    assert sistema._meta.get_field("cadastrador")


def test_atributo_cidade_de_um_SistemaCultura():

    sistema = SistemaCultura()

    assert sistema._meta.get_field("cidade")


def test_atributo_uf_de_um_SistemaCultura():

    sistema = SistemaCultura()

    assert sistema._meta.get_field("uf")


def test_atributo_data_criacao_de_um_SistemaCultura():

    sistema = SistemaCultura()

    assert sistema._meta.get_field('data_criacao')


def test_timezone_now_data_criacao_SistemaCultura():

    sistema = SistemaCultura()

    assert sistema.data_criacao.replace(second=0, microsecond=0) ==\
        timezone.now().replace(second=0, microsecond=0)


def test_SistemaCultura_save_cria_nova_instancia():
    """
    SistemaCultura deve sempre retornar uma nova instancia quando da tentativa
    de salvar os dados de uma instancia existente.
    """

    sistema = mommy.make("SistemaCultura", _fill_optional=['cidade', 'uf',
                                                           'cadastrador'])
    user = mommy.make("Usuario")

    sistema.cadastrador = user
    sistema.save()

    assert SistemaCultura.objects.count() == 2

    user.delete()
    [sistema.delete() for sistema in SistemaCultura.objects.all()]


def test_alterar_cadastrador_SistemaCultura(plano_trabalho):
    """ Testa método alterar_cadastrador da model SistemaCultura"""

    cadastrador_atual = plano_trabalho.usuario
    uf = cadastrador_atual.municipio.estado
    user = mommy.make("Usuario")
    sistema = mommy.make("SistemaCultura", cadastrador=cadastrador_atual, uf=uf)

    sistema.cadastrador = user
    sistema.save()

    assert SistemaCultura.objects.count() == 2
    assert SistemaCultura.historico.last().cadastrador == cadastrador_atual
    assert SistemaCultura.historico.first().cadastrador == user
    assert Municipio.objects.first().usuario == user
    assert PlanoTrabalho.objects.first().usuario == user
    assert Secretario.objects.first().usuario == user
    assert Responsavel.objects.first().usuario == user
    assert (
        sistema.cadastrador.data_publicacao_acordo
        == cadastrador_atual.data_publicacao_acordo
    )
    assert sistema.cadastrador.estado_processo == cadastrador_atual.estado_processo

    sistema.delete()
    user.delete()


@pytest.mark.skip
def test_limpa_cadastrador_alterado_SistemaCultura():
    """ Testa método para limpar referências de um cadastrador para os outos
    componentes do sistema de adesão """

    cadastrador = mommy.make(
        "Usuario",
        _fill_optional=["secretario", "responsavel", "plano_trabalho", "municipio"],
    )

    cadastrador.limpa_cadastrador()

    assert cadastrador.plano_trabalho is None
    assert cadastrador.municipio is None
    assert cadastrador.secretario is None
    assert cadastrador.responsavel is None
    # assert cadastrador.user.is_active is False

    cadastrador.secretario.delete()
    cadastrador.responsavel.delete()
    cadastrador.plano_trabalho.delete()
    cadastrador.municipio.delete()


def test_retorna_ativo_SistemaCultura_filtrado_por_uf():
    """ Retorna o último Sistema cultura criado sendo ele o ativo de
    uma UF específica """

    mommy.make('SistemaCultura',
               data_criacao=datetime(2018, 2, 3, 0, tzinfo=timezone.utc),
               _fill_optional=['uf'])
    sistema_ativo = mommy.make('SistemaCultura', _fill_optional=['uf'])

    assert SistemaCultura.sistema.get(uf=sistema_ativo.uf) == sistema_ativo

    SistemaCultura.objects.all().delete()


def test_retorna_ativo_SistemaCultura_filtrado_por_uf_e_cidade():
    """ Retorna o último Sistema cultura criado sendo ele o ativo de uma
    UF e cidade específicas """

    mommy.make('SistemaCultura',
               data_criacao=datetime(2018, 2, 3, 0, tzinfo=timezone.utc),
               _fill_optional=['uf', 'cidade'])
    sistema_ativo = mommy.make('SistemaCultura', _fill_optional=['uf', 'cidade'])

    assert SistemaCultura.sistema.get(
            uf=sistema_ativo.uf, cidade=sistema_ativo.cidade) == sistema_ativo


def test_alterar_cadastrador_sistema_cultura_sem_cadastrador():
    """ Testa alterar o cadastrador de um sistema cultura que não possui um
    cadastrador """
    sistema = mommy.make('SistemaCultura')
    cadastrador = mommy.make('Usuario')

    sistema.cadastrador = cadastrador
    sistema.save()
    sistema.refresh_from_db()

    assert sistema.cadastrador == cadastrador

    cadastrador.delete()
    sistema.delete()

    
def test_criar_plano_trabalho_para_Usuario_estado_processo():
    """ Criar um plano trabalho para um Usuario caso o estado do processo
    seja '6', que significa publicado no DOU """

    usuario = mommy.make('Usuario')

    usuario.estado_processo = '6'
    usuario.save()

    assert usuario.plano_trabalho

    usuario.plano_trabalho.delete()
    usuario.delete()


def test_ativo_ou_cria_SistemaCultura_ativo():
    """ Testa método ativo_ou_cria do manager SistemaCulturaManager
    retorna SistemaCultura ativo """

    mommy.make('SistemaCultura',
               data_criacao=datetime(2018, 2, 3, 0, tzinfo=timezone.utc),
               _fill_optional=['uf', 'cidade'])
    sistema_ativo = mommy.make('SistemaCultura', _fill_optional=['uf', 'cidade'])

    sistema, criado = SistemaCultura.sistema.get_or_create(cidade=sistema_ativo.cidade)
    assert sistema == sistema_ativo


def test_ativo_ou_cria_SistemaCultura_cria():
    """ Testa método ativo_ou_cria do manager SistemaCulturaManager
    retorna um novo sistema cultura """
    cidade = mommy.make('Cidade')
    uf = cidade.uf

    sistema, criado = SistemaCultura.sistema.get_or_create(cidade=cidade, uf=uf)

    assert isinstance(sistema, SistemaCultura)
    assert sistema.pk
    assert sistema.uf == uf
    assert sistema.cidade == cidade


@pytest.mark.skip("Depende de uma melhoria em EnteFederado")
def test_por_municipio_SistemaCultura_cidade():
    """ Testa se o método por município retorna os sistemas cultura de uma cidade """
    cidade = mommy.make('Cidade')
    uf = cidade.uf
    sistema = mommy.make("SistemaCultura", cidade=cidade, uf=uf)

    sistemas_cidade = SistemaCultura.objects.por_municipio(cidade=cidade, uf=uf)

    assert sistemas_cidade.count() == 1
    assert sistemas_cidade.first() == sistema


@pytest.mark.skip("Depende de uma melhoria em EnteFederado")
def test_por_municipio_SistemaCultura_uf():
    """ Testa se o método por município retorna os sistemas cultura de uma uf """
    uf = mommy.make('Uf')
    sistema = mommy.make("SistemaCultura", uf=uf)

    sistemas_cidade = SistemaCultura.objects.por_municipio(uf=uf)

    assert sistemas_cidade.count() == 1
    assert sistemas_cidade.first() == sistema


def test_alterar_cadastrador_sistema_cultura_sem_cadastrador():
    """ Testa alterar o cadastrador de um sistema cultura que não possui um
    cadastrador """
    sistema = mommy.make('SistemaCultura')
    cadastrador = mommy.make('Usuario')

    sistema.cadastrador = cadastrador
    sistema.save()
    sistema.refresh_from_db()

    assert sistema.cadastrador == cadastrador


def test_alterar_cadastrador_municipio_sem_cadastrador_previo():
    """
    Tenta alterar o cadastrador de um Municipio que ainda não possui
    cadastrador
    """

    cadastrador = mommy.make('Usuario')
    municipio = mommy.make('Municipio')
    sistema = mommy.make('SistemaCultura', cidade=municipio.cidade, uf=municipio.estado)

    sistema.cadastrador = cadastrador
    sistema.save()

    assert sistema.cadastrador == cadastrador

    municipio.refresh_from_db()
    assert municipio.usuario == cadastrador

    cadastrador.delete()
    SistemaCultura.objects.all().delete()
    municipio.delete()

@pytest.mark.parametrize('tipo', range(5))
def test_criar_componente_lei_sistema(tipo):
    """ Testa criar um novo componente Legislacao para um SistemaCultura """
    
    SistemaCultura.objects.all().delete()

    cadastrador = mommy.make("Usuario")
    sistema = mommy.make("SistemaCultura", cadastrador=cadastrador)

    legislacao = mommy.make("Componente", tipo=tipo)

    sistema.legislacao = legislacao
    sistema.save()

    sistemas = SistemaCultura.objects.count()

    assert sistemas == 2

    legislacao.delete()
    SistemaCultura.objects.all().delete()
    cadastrador.delete()


def test_criacao_funcionario(client):
    """
    Verifica se é possível criar um novo funcionario.
    """

    secretario = mommy.make("Funcionario", tipo_funcionario=0)
    responsavel = mommy.make("Funcionario", tipo_funcionario=1)
    sistema = mommy.make("SistemaCultura", secretario=secretario, responsavel=responsavel)
  
    assert SistemaCultura.objects.get(pk=sistema.pk) == sistema

    Funcionario.objects.all().delete()
    SistemaCultura.objects.all().delete()


def test_criacao_sede(client):
    """
    Verifica se é possível criar uma nova sede.
    """

    sede = mommy.make("Sede")
    sistema = mommy.make("SistemaCultura", sede=sede)
  
    assert SistemaCultura.objects.get(pk=sistema.pk) == sistema

    Sede.objects.all().delete()
    SistemaCultura.objects.all().delete()


def test_criacao_gestor(client):
    """
    Verifica se é possível criar um novo gestor.
    """

    gestor = mommy.make("Gestor", tipo_funcionario=2)
    sistema = mommy.make("SistemaCultura", gestor=gestor)
  
    assert SistemaCultura.objects.get(pk=sistema.pk) == sistema

    Gestor.objects.all().delete()
    SistemaCultura.objects.all().delete()


@pytest.mark.xfail
def test_entidade_ente_federado():
    """
    Testa a existencia da entidade EnteFederado
    """

    with pytest.raises(ImportError):
        from adesao.models import EnteFederado


@pytest.mark.skip("Necessário buscar uma estratégia melhor para testar o atributos da model.")
def test_campos_entidade_EnteFederado():
    """
    Testa a existenca das seguintes propriedades em uma instacia de
    EnteFederado: ("cod_ibge", "nome", "mandatario", "territorio", "populacao",
    "densidade", "idh", "receita", "despesas", "pib")
    """

    from adesao.models import EnteFederado

    campos = ("cod_ibge", "nome", "mandatario", "territorio", "populacao", "densidade",
            "idh", "receita", "despesas", "pib")

    assert campos in set(EnteFederado._meta.fields)
