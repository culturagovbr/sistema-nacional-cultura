import pytest
from datetime import date

from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model

from model_mommy import mommy

from planotrabalho.models import SituacoesArquivoPlano
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
                         _fill_optional=['secretario', 'responsavel'])

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
    conselho_cultural = mommy.make('ConselhoCultural', situacao_ata=situacao)
    fundo_cultura = mommy.make('FundoCultura', situacao_lei_plano=situacao)
    plano_cultura = mommy.make('PlanoCultura', situacao_lei_plano=situacao)
    lei_sistema = mommy.make('CriacaoSistema', situacao_lei_sistema=situacao)
    orgao_gestor = mommy.make('OrgaoGestor', situacao_relatorio_secretaria=situacao)
    conselheiro = mommy.make('Conselheiro', conselho=conselho_cultural)
    plano_trabalho = mommy.make('PlanoTrabalho',
                                conselho_cultural=conselho_cultural,
                                fundo_cultura=fundo_cultura,
                                criacao_sistema=lei_sistema,
                                orgao_gestor=orgao_gestor,
                                plano_cultura=plano_cultura)
    ente_federado = mommy.make('Municipio')

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
