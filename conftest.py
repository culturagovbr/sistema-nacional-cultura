import pytest
from datetime import date

from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model

from model_mommy import mommy

from model_mommy.recipe import Recipe

from planotrabalho.models import SituacoesArquivoPlano
from adesao.models import EnteFederado
from adesao.models import Usuario


@pytest.fixture(autouse=True, scope='session')
def situacoes(django_db_setup, django_db_blocker):
    """
    Cria situações dos arquivos do Plano Trabalho enviados no banco de testes
    """
    with django_db_blocker.unblock():

        situacoes = (
            (0, 'Em preenchimento'),
            (1, 'Avaliando anexo'),
            (2, 'Concluída'),
            (3, 'Arquivo aprovado com ressalvas'),
            (4, 'Arquivo danificado'),
            (5, 'Arquivo incompleto'),
            (6, 'Arquivo incorreto'),
        )

        for situacao in situacoes:
            SituacoesArquivoPlano.objects.create(id=situacao[0], descricao=situacao[1])

        yield

        SituacoesArquivoPlano.objects.all().delete()


@pytest.fixture(autouse=True, scope="session")
def ente_federado(django_db_setup, django_db_blocker):

    ufs = {
            11: "RO",
            12: "AC",
            13: "AM",
            14: "RR",
            15: "PA",
            16: "AP",
            17: "TO",
            21: "MA",
            22: "PI",
            23: "CE",
            24: "RN",
            25: "PB",
            26: "PE",
            27: "AL",
            28: "SE",
            29: "BA",
            31: "MG",
            32: "ES",
            33: "RJ",
            35: "SP",
            41: "PR",
            42: "SC",
            43: "RS",
            50: "MS",
            51: "MT",
            52: "GO",
            53: "DF"
            }

    with django_db_blocker.unblock():
        for cod, uf in ufs.items():
            mommy.make("EnteFederado", cod_ibge=cod, nome=uf)

        yield

        EnteFederado.objects.all().delete()


@pytest.fixture(scope='function')
def login(client):
    """
    Cria um usuário fake comum
    """

    User = get_user_model()
    user = User.objects.create(username='teste', email='user@mail.com')
    user.set_password('123456')
    user.save()
    usuario = mommy.make('Usuario', user=user,
                         _fill_optional=['secretario', 'responsavel',
                                         'data_publicacao_acordo'])

    login = client.login(username=user.username, password='123456')

    yield usuario

    client.logout()
    usuario.secretario.delete()
    usuario.responsavel.delete()
    usuario.delete()
    user.delete()


@pytest.fixture
def login_staff(client):
    """
    Cria um usuário fake com is_staff=True, com permissões de administrador
    """

    User = get_user_model()
    user = User.objects.create(username='staff', is_staff=True,
                               email='staff@mail.com')
    user.set_password('123456')

    user.save()
    usuario = mommy.make('Usuario', user=user)

    login = client.login(username=user.username, password='123456')

    return usuario


@pytest.fixture(scope='function')
def plano_trabalho(login):
    """
    Cria um plano de trabalho associado a um usuário comum.
    """

    usuario = login
    situacao = SituacoesArquivoPlano.objects.first()
    conselho_cultural = mommy.make('ConselhoCultural')
    conselho = mommy.make("ConselhoDeCultura", tipo=3)
    fundo_cultura = mommy.make('FundoCultura')
    plano_cultura = mommy.make('PlanoCultura')
    lei_sistema = mommy.make('CriacaoSistema')
    orgao_gestor = mommy.make('OrgaoGestor')
    conselheiro = mommy.make('Conselheiro', conselho=conselho)
    plano_trabalho = mommy.make('PlanoTrabalho',
                                conselho_cultural=conselho_cultural,
                                fundo_cultura=fundo_cultura,
                                criacao_sistema=lei_sistema,
                                orgao_gestor=orgao_gestor,
                                plano_cultura=plano_cultura)
    ente_federado = mommy.make('Municipio', _fill_optional=['cidade'])

    usuario.municipio = ente_federado
    usuario.plano_trabalho = plano_trabalho
    usuario.data_publicacao_acordo = date.today()
    usuario.save()

    componentes = (
        'fundo_cultura',
        'plano_cultura',
        'criacao_sistema',
        'orgao_gestor',
        'conselho_cultural'
        )

    arquivo = SimpleUploadedFile("lei.txt", b"file_content", content_type="text/plain")
    for componente in componentes:
        comp = getattr(plano_trabalho, componente)
        comp.arquivo = arquivo
        comp.situacao = SituacoesArquivoPlano.objects.get(pk=1)
        comp.save()

    yield plano_trabalho

    plano_trabalho.delete()
    conselho_cultural.delete()
    fundo_cultura.delete()
    plano_cultura.delete()
    lei_sistema.delete()
    orgao_gestor.delete()
    conselheiro.delete()
    ente_federado.delete()


@pytest.fixture(scope='function')
def sistema_cultura():

    ente_federado = mommy.make("EnteFederado", cod_ibge=111, _fill_optional=True, nome="Bahia")

    conselho = mommy.make("ConselhoDeCultura", tipo=3, _fill_optional=True)

    conselheiros = mommy.make("Conselheiro", _quantity=3, conselho=conselho, situacao=1, _fill_optional=True)

    sistema_cultura = mommy.make(
            "SistemaCultura",
            estado_processo=6,
            ente_federado=ente_federado,
            conselho=conselho,
            _fill_optional=True
            )

    yield sistema_cultura

    sistema_cultura.delete()

