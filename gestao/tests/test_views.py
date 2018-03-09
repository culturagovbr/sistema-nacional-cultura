import pytest
import datetime

from django.core.urlresolvers import resolve
from django.core.urlresolvers import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from model_mommy import mommy

from gestao.views import diligencia_view
from gestao.forms import DiligenciaForm

from gestao.models import Diligencia
from adesao.models import Municipio
from planotrabalho.models import OrgaoGestor
from planotrabalho.models import CriacaoSistema
from planotrabalho.models import FundoCultura
from planotrabalho.models import PlanoCultura
from planotrabalho.models import ConselhoCultural
from planotrabalho.models import SituacoesArquivoPlano

pytestmark = pytest.mark.django_db


@pytest.fixture
def situacoes():
    """Cria situações dos arquivos do Plano Trabalho enviados no banco de testes"""
    situacoes = (
        (0, 'Em preenchimento'),
        (1, 'Avaliando anexo'),
        (2, 'Concluída'),
        (3, 'Arquivo aprovado com ressalvas'),
        (4, 'Arquivo danificado'),
        (5, 'Arquivo incompleto'),
        (6, 'Arquivo incorreto')
    )

    for situacao in situacoes:
        SituacoesArquivoPlano.objects.create(id=situacao[0], descricao=situacao[1])

    return SituacoesArquivoPlano.objects.all()


@pytest.fixture
def login(client):
    user = User.objects.create(username='teste')
    user.set_password('123456')
    user.save()
    usuario = mommy.make('Usuario', user=user)

    login = client.login(username=user.username, password='123456')

    return usuario


@pytest.fixture
def login_staff(client):
    user = User.objects.create(username='staff', is_staff=True)
    user.set_password('123456')

    user.save()
    usuario = mommy.make('Usuario', user=user)

    login = client.login(username=user.username, password='123456')

    return usuario


def arquivo_componentes(plano_trabalho, situacoes):
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

    return plano_trabalho


@pytest.fixture
def plano_trabalho(login, situacoes):
    fundo_cultura = mommy.make("FundoCultura")
    plano_cultura = mommy.make("PlanoCultura")
    orgao_gestor = mommy.make("OrgaoGestor")
    conselho_cultural = mommy.make("ConselhoCultural")
    lei_sistema = mommy.make("CriacaoSistema")

    ente_federado = mommy.make('Municipio')

    plano_trabalho = mommy.make("PlanoTrabalho", fundo_cultura=fundo_cultura,
                                plano_cultura=plano_cultura, orgao_gestor=orgao_gestor,
                                conselho_cultural=conselho_cultural, criacao_sistema=lei_sistema)

    login.municipio = ente_federado
    login.plano_trabalho = plano_trabalho
    login.save()

    plano_trabalho = arquivo_componentes(plano_trabalho, situacoes)

    return plano_trabalho


@pytest.fixture
def url():
    """Retorna uma string contendo a URL preparada para ser formatada."""

    return "/gestao/{id}/diligencia/{componente}/{resultado}"


def test_url_diligencia_retorna_200(url, client, plano_trabalho, login_staff):
    """Testa se há url referente à página de diligências.
        A url teria o formato: gestao/id_plano_trabalho/diligencia/componente_plano_trabalho"""

    request = client.get(url.format(id=plano_trabalho.id, componente='plano_cultura', resultado='0'))

    assert request.status_code == 200


def test_resolve_url_atraves_sua_view_name(url, client, plano_trabalho):
    """Testa se o Django retorna a url através da sua view_name"""

    resolved = resolve(url.format(id=plano_trabalho.id, componente='plano_cultura', resultado='0'))

    assert resolved.url_name == "diligencia_componente"
    assert resolved.kwargs['pk'] == str(plano_trabalho.id)


def test_recepcao_componente_na_url_diligencia(url, client, plano_trabalho):
    """Testa se a url esta recebendo o componente correspondente a diligencia que sera escrita"""

    resolved = resolve(url.format(id=plano_trabalho.id, componente="lei_sistema", resultado='0'))

    assert resolved.kwargs["componente"] == "lei_sistema"


def test_url_componente_retorna_200(url, client, plano_trabalho, login_staff):
    """Testa se a url retorna 200 ao acessar um componente"""

    request = client.get(url.format(id=plano_trabalho.id, componente="fundo_cultura", resultado='0'))

    assert request.status_code == 200


def test_url_retorna_404_caso_componente_nao_exista(url, client, plano_trabalho, login_staff):
    """Testa se a URL retorna 404 caso o componente não exista"""

    request = client.get(url.format(id=plano_trabalho.id, componente="um_componente_qualquer", resultado='0'))

    assert request.status_code == 404


def test_renderiza_template(url, client, plano_trabalho, login_staff):
    """ Testa se o método da view renderiza um template"""

    request = client.get(url.format(id=plano_trabalho.id, componente="criacao_sistema", resultado='0'))
    assert request.content


def test_renderiza_template_diligencia(url, client, plano_trabalho, login_staff):
    """Testa se o template específico da diligência é renderizado corretamente"""

    request = client.get(url.format(id=plano_trabalho.id, componente="conselho_cultural", resultado='0'))
    assert "gestao/diligencia/diligencia.html" == request.templates[0].name


def test_existencia_do_contexto_view(url, client, plano_trabalho, login_staff):
    """Testa se o contexto existe no retorno da view """

    contexts = [
        'ente_federado',
        'arquivo',
        'data_envio',
        'historico_diligencias',
    ]

    request = client.get(url.format(id=plano_trabalho.id, componente="conselho_cultural", resultado='0'))

    for context in contexts:
        assert context in request.context


def test_valor_context_retornado_na_view(url, client, plano_trabalho, login_staff):
    """Testa se há informações retornadas na view"""

    request = client.get(url.format(id=plano_trabalho.id, componente="fundo_cultura", resultado='0'))

    contexts = [
        'ente_federado',
        'arquivo',
        'data_envio',
        'historico_diligencias',
        'usuario_id'
    ]
    for context in contexts:
        assert request.context[context] != ''


def test_retorno_400_post_criacao_diligencia(url, client, plano_trabalho, login_staff):
    """ Testa se o status do retorno é 400 para requests sem os parâmetros esperados """

    request = client.post(url.format(id=plano_trabalho.id, componente="orgao_gestor", resultado='0'),
                          data={'bla': ''})

    assert request.status_code == 400


def test_retorna_400_POST_classificacao_inexistente(url, rf, plano_trabalho, login_staff):
    """
    Testa se o status do retorno é 400 quando feito um POST com a classificao invalida
    de um arquivo.
    """
    request = rf.post(url.format(id=plano_trabalho.id, componente="orgao_gestor", resultado='0'),
                      data={'classificacao_arquivo': ''})
    user = login_staff.user
    request.user = user

    response = diligencia_view(request, plano_trabalho.id, "orgao_gestor", "0")

    assert response.status_code == 400


def test_form_diligencia_utlizado_na_diligencia_view(url, client, plano_trabalho, login_staff):
    """Testa que existe um form no context da diligência view """

    request = client.get(url.format(id=plano_trabalho.id, componente="orgao_gestor", resultado='0'))

    assert request.context['form']


def test_tipo_do_form_utilizado_na_diligencia_view(url, client, plano_trabalho, login_staff):
    """ Testa se o form utilizado na diligencia_view é do tipo DiligenciaForm """

    request = client.get(url.format(id=plano_trabalho.id, componente="orgao_gestor", resultado='0'))

    assert isinstance(request.context['form'], DiligenciaForm)


def test_invalido_form_para_post_diligencia(url, client, plano_trabalho, login_staff):
    """ Testa se o form invalida post com dados errados """

    request = client.post(url.format(id=plano_trabalho.id, componente="orgao_gestor", resultado='0'),
                          data={"classificacao_arquivo": "", "texto_diligencia": ''})

    assert request.status_code == 400


def test_obj_ente_federado(url, client, plano_trabalho, login_staff):
    """ Testa se o objeto retornado ente_federado é uma String"""

    request = client.get(url.format(id=plano_trabalho.id, componente='orgao_gestor', resultado='0'))

    assert isinstance(request.context['ente_federado'], str)
    assert request.context['ente_federado'] == plano_trabalho.usuario.municipio.estado.sigla


def test_404_para_plano_trabalho_invalido_diligencia(url, client, login_staff):
    """ Testa se a view da diligência retorna 404 para um plano de trabalho inválido """

    request = client.get(url.format(id='7', componente='orgao_gestor', resultado='0'))

    assert request.status_code == 404


def test_ente_federado_retornado_na_diligencia(url, client, plano_trabalho, login_staff):
    """
    Testa se ente_federado retornado está relacionado com o plano trabalho passado como parâmetro
    """

    request = client.get(url.format(id=plano_trabalho.id, componente='conselho_cultural', resultado='0'))

    assert request.context['ente_federado'] == plano_trabalho.usuario.municipio.estado.sigla


def test_salvar_informacoes_no_banco(url, client, plano_trabalho, login_staff, situacoes):
    """Testa se as informacoes validadas pelo form estao sendo salvas no banco"""

    response = client.post(url.format(id=plano_trabalho.id, componente="orgao_gestor", resultado='0'),
                           data={'classificacao_arquivo': '4',
                                 'texto_diligencia': 'bla'})
    diligencia = Diligencia.objects.first()

    assert Diligencia.objects.count() == 1
    assert diligencia.texto_diligencia == 'bla'
    assert diligencia.classificacao_arquivo.id == 4
    assert isinstance(diligencia.componente, OrgaoGestor)


def test_redirecionamento_de_pagina_apos_POST(url, client, plano_trabalho, login_staff, situacoes):
    """ Testa se há o redirecionamento de página após o POST da diligência """

    request = client.post(url.format(id=plano_trabalho.id, componente="orgao_gestor", resultado='0'),
                          data={"classificacao_arquivo": "4", "texto_diligencia": 'Ta errado cara'})
    url_redirect = request.url.split('http://testserver/')

    assert url_redirect[1] == 'gestao/detalhar/municipio/{}'.format(plano_trabalho.usuario.id)
    assert request.status_code == 302


def test_arquivo_enviado_pelo_componente(url, client, plano_trabalho, login_staff):
    """ Testa se o arquivo enviado pelo componente está correto """

    arquivo = plano_trabalho.conselho_cultural.arquivo

    request = client.get(url.format(id=plano_trabalho.id, componente="conselho_cultural", resultado='0'))

    assert request.context['arquivo'] == arquivo


def test_arquivo_enviado_salvo_no_diretorio_do_componente(url, client, plano_trabalho, login):
    """ Testa se o arquivo enviando pelo componente está sendo salvo no
    diretório especifico dentro da pasta do ente federado."""

    arquivo = plano_trabalho.fundo_cultura.arquivo

    assert arquivo.url == '/media/{id}/docs/{componente}/{arquivo}'.format(id=login.municipio.id,
                                                                          componente=plano_trabalho.fundo_cultura._meta.object_name.lower(),
                                                                          arquivo=plano_trabalho.fundo_cultura.arquivo.name.split('/')[3])


def test_exibicao_historico_diligencia(url, client, plano_trabalho, login_staff):
    """Testa se o histórico de diligências é retornado pelo contexto"""

    diligencia = mommy.make('Diligencia', _quantity=4, componente=plano_trabalho.orgao_gestor)
    diligencias = plano_trabalho.orgao_gestor.diligencias.all().order_by('-data_criacao')[:3]

    request = client.get(url.format(id=plano_trabalho.id, componente="orgao_gestor", resultado='0'))
    diferenca_listas = set(diligencias).symmetric_difference(set(request.context['historico_diligencias']))
    assert diferenca_listas == set()


def test_captura_nome_usuario_logado_na_diligencia(url, client, plano_trabalho, login_staff, situacoes):
    """
        Testa se o nome do usuario logado é capturado assim que uma diligencia for feita
    """

    request = client.post(url.format(id=plano_trabalho.id, componente="orgao_gestor", resultado='0'), data={"classificacao_arquivo": "4", "texto_diligencia": "Muito legal"})

    diligencia = Diligencia.objects.last()

    assert diligencia.usuario == login_staff


def test_muda_situacao_arquivo_componente(url, client, situacoes, plano_trabalho, login_staff):
    """ Testa se ao realizar o post da diligência a situação do arquivo do componente é alterada """

    request = client.post(url.format(id=plano_trabalho.id, componente="orgao_gestor", resultado='0'), data={"classificacao_arquivo": 4, "texto_diligencia": "Não vai rolar"})

    assert OrgaoGestor.objects.first().situacao.id == 4


def test_retorno_200_para_detalhar_municipio(client, plano_trabalho, login_staff):
    """ Testa se página de detalhamento do município retorna 200 """

    usuario_id = plano_trabalho.usuario.id
    request = client.get('/gestao/detalhar/municipio/{}'.format(usuario_id))
    assert request.status_code == 200


def test_retorno_do_form_da_diligencia(url, client, plano_trabalho, situacoes, login_staff):
    """ Testa se form retornado no contexto tem as opções corretas dependendo do tipo de resultado"""

    request_aprova = client.get(url.format(id=plano_trabalho.id, componente='orgao_gestor', resultado=1))
    request_recusa = client.get(url.format(id=plano_trabalho.id, componente='orgao_gestor', resultado=0))

    classificacao_aprova = set(request_aprova.context['form'].fields['classificacao_arquivo'].queryset)
    classificacao_recusa = set(request_recusa.context['form'].fields['classificacao_arquivo'].queryset)

    assert classificacao_aprova.symmetric_difference(SituacoesArquivoPlano.objects.filter(pk=2)) == set()
    assert classificacao_recusa.symmetric_difference(SituacoesArquivoPlano.objects.filter(id__gte=4, id__lte=6)) == set()


def usuario_id_retornado_pelo_context_diligencia(url, client, plano_trabalho, login_staff):
    """ Testa se o id do usuário enviado pelo context está correto """

    request = client.get(url.format(id=plano_trabalho.id, componente="orgao_gestor", resultado='0'))

    assert request.context['usuario_id'] == plano_trabalho.usuario.id


def test_criacao_diligencia_exclusiva_para_gestor(client, url, plano_trabalho, login):
    """Testa se ao tentar acessar a url de criação da diligência o usuário
    que não é autorizado é redirecionado para a tela de login"""

    url_diligencia = url.format(id=plano_trabalho.id, componente="orgao_gestor", resultado='1')

    request = client.get(url_diligencia)

    url_redirect = request.url.split('http://testserver/')
    url_login = "admin/login/?next={}".format(url_diligencia)

    assert request.status_code == 302
    assert url_redirect[1] == url_login


def test_inserir_documentos_orgao_gestor(client, plano_trabalho, login_staff):
    """ Testa se funcionalidade de inserir documento para orgão gestor na
    tela de gestão salva no field arquivo """

    arquivo = SimpleUploadedFile("orgao.txt", b"file_content", content_type="text/plain")

    url = reverse('gestao:alterar_orgao', kwargs={'pk': plano_trabalho.orgao_gestor.id})

    client.post(url, data={'arquivo': arquivo})

    name = OrgaoGestor.objects.first().arquivo.name.split('orgaogestor/')[1]

    assert name == arquivo.name


def test_inserir_documentos_criacao_sistema(client, plano_trabalho, login_staff):
    """ Testa se funcionalidade de inserir documento para sistema de cultura na
    tela de gestão salva no field arquivo """

    arquivo = SimpleUploadedFile("sistema_cultura.txt", b"file_content", content_type="text/plain")

    url = reverse('gestao:alterar_sistema', kwargs={'pk': plano_trabalho.criacao_sistema.id})

    client.post(url, data={'arquivo': arquivo})

    name = CriacaoSistema.objects.first().arquivo.name.split('criacaosistema/')[1]

    assert name == arquivo.name


def test_inserir_documentos_fundo_cultura(client, plano_trabalho, login_staff):
    """ Testa se funcionalidade de inserir documento para na fundo de cultura na
    tela de gestão salva no field arquivo """

    arquivo = SimpleUploadedFile("fundo_cultura.txt", b"file_content", content_type="text/plain")

    url = reverse('gestao:alterar_fundo', kwargs={'pk': plano_trabalho.fundo_cultura.id})

    client.post(url, data={'arquivo': arquivo})

    name = FundoCultura.objects.first().arquivo.name.split('fundocultura/')[1]

    assert name == arquivo.name


def test_inserir_documentos_plano_cultura(client, plano_trabalho, login_staff):
    """ Testa se funcionalidade de inserir documento para plano de cultura na
    tela de gestão salva no field arquivo """

    arquivo = SimpleUploadedFile("plano_cultura.txt", b"file_content", content_type="text/plain")

    url = reverse('gestao:alterar_plano', kwargs={'pk': plano_trabalho.plano_cultura.id})

    client.post(url, data={'arquivo': arquivo})

    name = PlanoCultura.objects.first().arquivo.name.split('planocultura/')[1]

    assert name == arquivo.name


def test_inserir_documentos_conselho_cultural(client, plano_trabalho, login_staff):
    """ Testa se funcionalidade de inserir documento para conselho cultural na
    tela de gestão salva no field arquivo """

    arquivo = SimpleUploadedFile("conselho_cultural.txt", b"file_content", content_type="text/plain")

    url = reverse('gestao:alterar_conselho', kwargs={'pk': plano_trabalho.conselho_cultural.id})

    client.post(url, data={'arquivo': arquivo})

    name = ConselhoCultural.objects.first().arquivo.name.split('conselhocultural/')[1]

    assert name == arquivo.name
