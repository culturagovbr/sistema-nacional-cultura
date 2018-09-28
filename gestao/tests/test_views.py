import datetime
import json
import pytest

from django.urls import resolve
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core import mail

from model_mommy import mommy

# from gestao.forms import DiligenciaComponenteForm

from gestao.models import DiligenciaSimples
from adesao.models import Uf
from adesao.models import Usuario
from adesao.models import SistemaCultura

from planotrabalho.models import Componente
from planotrabalho.models import OrgaoGestor
from planotrabalho.models import CriacaoSistema
from planotrabalho.models import FundoCultura
from planotrabalho.models import PlanoCultura
from planotrabalho.models import ConselhoCultural
from planotrabalho.models import SituacoesArquivoPlano
from planotrabalho.models import PlanoTrabalho

from gestao.views import AlterarCadastrador


pytestmark = pytest.mark.django_db


@pytest.fixture
def url():
    """Retorna uma string contendo a URL preparada para ser formatada."""

    return "/gestao/{id}/diligencia/{componente}/{resultado}"


def test_url_diligencia_retorna_200(url, client, login_staff):
    """
    Testa se há url referente à página de diligências.
    A url teria o formato: gestao/id_sistema_cultura/diligencia/componente_plano_trabalho
    """
    orgao_gestor = mommy.make("Componente", tipo=1, situacao=1)
    sistema_cultura = mommy.make("SistemaCultura", _fill_optional=['ente_federado',
        'cadastrador'], orgao_gestor=orgao_gestor)

    arquivo = SimpleUploadedFile("lei.txt", b"file_content", content_type="text/plain")
    orgao_gestor.arquivo = arquivo
    orgao_gestor.save()

    request = client.get(
        url.format(id=sistema_cultura.pk, componente="orgao_gestor", resultado="1")
    )

    assert request.status_code == 200


def test_resolve_url_atraves_sua_view_name(url, client, plano_trabalho):
    """Testa se o Django retorna a url através da sua view_name"""

    resolved = resolve(
        url.format(id=plano_trabalho.id, componente="plano_cultura", resultado="0")
    )

    assert resolved.url_name == "diligencia_componente"
    assert resolved.kwargs["pk"] == plano_trabalho.id


def test_recepcao_componente_na_url_diligencia(url, client, plano_trabalho):
    """Testa se a url esta recebendo o componente correspondente a diligencia que sera escrita"""

    resolved = resolve(
        url.format(id=plano_trabalho.id, componente="lei_sistema", resultado="0")
    )

    assert resolved.kwargs["componente"] == "lei_sistema"


def test_url_componente_retorna_200(url, client, login_staff):
    """Testa se a url retorna 200 ao acessar um componente"""

    orgao_gestor = mommy.make("Componente", tipo=1, situacao=1)
    sistema_cultura = mommy.make("SistemaCultura", _fill_optional=['ente_federado',
        'cadastrador'], orgao_gestor=orgao_gestor)

    arquivo = SimpleUploadedFile("lei.txt", b"file_content", content_type="text/plain")
    orgao_gestor.arquivo = arquivo
    orgao_gestor.save()

    request = client.get(
        url.format(id=sistema_cultura.id, componente="orgao_gestor", resultado="0")
    )

    assert request.status_code == 200


def test_url_retorna_404_caso_componente_nao_exista(
    url, client, plano_trabalho, login_staff
):
    """Testa se a URL retorna 404 caso o componente não exista"""

    request = client.get(
        url.format(
            id=plano_trabalho.id, componente="um_componente_qualquer", resultado="0"
        )
    )

    assert request.status_code == 404


def test_renderiza_template(url, client, plano_trabalho, login_staff):
    """ Testa se o método da view renderiza um template"""

    request = client.get(
        url.format(id=plano_trabalho.id, componente="criacao_sistema", resultado="0")
    )
    assert request.content


def test_renderiza_template_diligencia(url, client, login_staff):
    """Testa se o template específico da diligência é renderizado corretamente"""

    conselho = mommy.make("Componente", tipo=3, situacao=1)
    sistema_cultura = mommy.make("SistemaCultura", _fill_optional=['ente_federado',
        'cadastrador'], conselho=conselho)

    arquivo = SimpleUploadedFile("conselho.txt", b"file_content", content_type="text/plain")
    conselho.arquivo = arquivo
    conselho.save()

    request = client.get(
        url.format(id=sistema_cultura.id, componente="conselho", resultado="0")
    )
    assert "diligencia.html" == request.templates[0].name


def test_existencia_do_contexto_view(url, client, login_staff):
    """Testa se o contexto existe no retorno da view """

    contexts = ["ente_federado", "arquivo", "data_envio", "historico_diligencias"]

    conselho = mommy.make("Componente", tipo=3, situacao=1)
    sistema_cultura = mommy.make("SistemaCultura", _fill_optional=['ente_federado',
        'cadastrador'], conselho=conselho)

    arquivo = SimpleUploadedFile("conselho.txt", b"file_content", content_type="text/plain")
    conselho.arquivo = arquivo
    conselho.save()

    request = client.get(
        url.format(id=sistema_cultura.id, componente="conselho", resultado="0")
    )

    for context in contexts:
        assert context in request.context


def test_valor_context_retornado_na_view(url, client, login_staff):
    """Testa se há informações retornadas na view"""

    fundo = mommy.make("Componente", tipo=2, situacao=1)
    sistema_cultura = mommy.make("SistemaCultura", _fill_optional=['ente_federado',
        'cadastrador'], fundo_cultura=fundo)

    arquivo = SimpleUploadedFile("conselho.txt", b"file_content", content_type="text/plain")
    fundo.arquivo = arquivo
    fundo.save()

    request = client.get(
        url.format(id=sistema_cultura.id, componente="fundo_cultura", resultado="0")
    )

    contexts = [
        "ente_federado",
        "arquivo",
        "data_envio",
        "historico_diligencias",
        "usuario_id",
    ]
    for context in contexts:
        assert request.context[context] != ""


def test_retorno_400_post_criacao_diligencia(url, client, login_staff):
    """ Testa se o status do retorno é 400 para requests sem os parâmetros esperados """

    orgao_gestor = mommy.make("Componente", tipo=1, situacao=1)
    sistema_cultura = mommy.make("SistemaCultura", _fill_optional=['ente_federado',
        'cadastrador'], orgao_gestor=orgao_gestor)

    arquivo = SimpleUploadedFile("lei.txt", b"file_content", content_type="text/plain")
    orgao_gestor.arquivo = arquivo
    orgao_gestor.save()

    request = client.post(
        url.format(id=sistema_cultura.id, componente="orgao_gestor", resultado="0"),
        data={"bla": ""},
    )

    assert request.status_code == 400


def test_retorna_400_POST_classificacao_inexistente(
    url, client, login_staff
):
    """
    Testa se o status do retorno é 400 quando feito um POST com a classificao invalida
    de um arquivo.
    """
    orgao_gestor = mommy.make("Componente", tipo=1, situacao=1)
    sistema_cultura = mommy.make("SistemaCultura", _fill_optional=['ente_federado',
        'cadastrador'], orgao_gestor=orgao_gestor)

    arquivo = SimpleUploadedFile("lei.txt", b"file_content", content_type="text/plain")
    orgao_gestor.arquivo = arquivo
    orgao_gestor.save()

    request = client.post(
        url.format(id=sistema_cultura.id, componente="orgao_gestor", resultado="0"),
        data={"classificacao_arquivo": ""},
    )
    user = login_staff.user
    request.user = user

    assert request.status_code == 400


def test_form_diligencia_utlizado_na_diligencia_view(
    url, client, login_staff
):
    """Testa que existe um form no context da diligência view """

    sistema_cultura = mommy.make("SistemaCultura", _fill_optional=['ente_federado',
        'cadastrador'])
    request = client.get(
        url.format(id=sistema_cultura.id, componente="plano_trabalho", resultado="0")
    )
    assert request.context["form"]


def test_tipo_do_form_utilizado_na_diligencia_view(
    url, client, login_staff
):
    """ Testa se o form utilizado na diligencia_view é do tipo DiligenciaForm """

    orgao_gestor = mommy.make("Componente", tipo=1, situacao=1)
    sistema_cultura = mommy.make("SistemaCultura", _fill_optional=['ente_federado',
        'cadastrador'], orgao_gestor=orgao_gestor)

    arquivo = SimpleUploadedFile("lei.txt", b"file_content", content_type="text/plain")
    orgao_gestor.arquivo = arquivo
    orgao_gestor.save()

    request = client.get(
        url.format(id=sistema_cultura.id, componente="orgao_gestor", resultado="0")
    )

    assert isinstance(request.context["form"], DiligenciaForm)


def test_invalido_form_para_post_diligencia(url, client, login_staff):
    """ Testa se o form invalida post com dados errados """

    orgao_gestor = mommy.make("Componente", tipo=1, situacao=1)
    sistema_cultura = mommy.make("SistemaCultura", _fill_optional=['ente_federado',
        'cadastrador'], orgao_gestor=orgao_gestor)

    arquivo = SimpleUploadedFile("lei.txt", b"file_content", content_type="text/plain")
    orgao_gestor.arquivo = arquivo
    orgao_gestor.save()

    request = client.post(
        url.format(id=sistema_cultura.id, componente="orgao_gestor", resultado="0"),
        data={"classificacao_arquivo": "", "texto_diligencia": ""},
    )

    assert request.status_code == 400


def test_obj_ente_federado(url, client, login_staff):
    """ Testa se o objeto retornado ente_federado é uma String"""

    orgao_gestor = mommy.make("Componente", tipo=1, situacao=1)
    sistema_cultura = mommy.make("SistemaCultura", _fill_optional=['ente_federado',
        'cadastrador'], orgao_gestor=orgao_gestor)

    arquivo = SimpleUploadedFile("lei.txt", b"file_content", content_type="text/plain")
    orgao_gestor.arquivo = arquivo
    orgao_gestor.save()

    request = client.get(
        url.format(id=sistema_cultura.id, componente="orgao_gestor", resultado="0")
    )

    assert isinstance(request.context["ente_federado"], str)
    assert request.context["ente_federado"] == sistema_cultura.ente_federado.nome


def test_404_para_plano_trabalho_invalido_diligencia(url, client, login_staff):
    """ Testa se a view da diligência retorna 404 para um plano de trabalho inválido """

    request = client.get(url.format(id="7", componente="orgao_gestor", resultado="0"))

    assert request.status_code == 404


def test_ente_federado_retornado_na_diligencia(
    url, client, login_staff
):
    """
    Testa se ente_federado retornado está relacionado com o plano trabalho passado como parâmetro
    """

    conselho = mommy.make("Componente", tipo=3, situacao=1)
    sistema_cultura = mommy.make("SistemaCultura", _fill_optional=['ente_federado',
        'cadastrador'], conselho=conselho)

    arquivo = SimpleUploadedFile("conselho.txt", b"file_content", content_type="text/plain")
    conselho.arquivo = arquivo
    conselho.save()

    request = client.get(
        url.format(id=sistema_cultura.id, componente="conselho", resultado="0")
    )

    assert request.context["ente_federado"] == sistema_cultura.ente_federado.nome


def test_salvar_informacoes_no_banco(url, client, login_staff):
    """Testa se as informacoes validadas pelo form estao sendo salvas no banco"""

    orgao_gestor = mommy.make("Componente", tipo=1, situacao=1)
    sistema_cultura = mommy.make("SistemaCultura", _fill_optional=['ente_federado',
        'cadastrador'], orgao_gestor=orgao_gestor)

    arquivo = SimpleUploadedFile("lei.txt", b"file_content", content_type="text/plain")
    orgao_gestor.arquivo = arquivo
    orgao_gestor.save()
    
    response = client.post(
        url.format(id=sistema_cultura.id, componente="orgao_gestor", resultado="0"),
        data={"classificacao_arquivo": "4", "texto_diligencia": "bla"},
    )
    diligencia = DiligenciaSimples.objects.first()

    assert DiligenciaSimples.objects.count() == 1
    assert diligencia.texto_diligencia == "bla"
    assert diligencia.classificacao_arquivo == 4


def test_redirecionamento_de_pagina_apos_POST(url, client, login_staff):
    """ Testa se há o redirecionamento de página após o POST da diligência """

    orgao_gestor = mommy.make("Componente", tipo=1, situacao=1)
    sistema_cultura = mommy.make("SistemaCultura", _fill_optional=['ente_federado',
        'cadastrador'], orgao_gestor=orgao_gestor)

    arquivo = SimpleUploadedFile("lei.txt", b"file_content", content_type="text/plain")
    orgao_gestor.arquivo = arquivo
    orgao_gestor.save()

    request = client.post(
        url.format(id=sistema_cultura.id, componente="orgao_gestor", resultado="0"),
        data={"classificacao_arquivo": "4", "texto_diligencia": "Ta errado cara"},
    )
    url_redirect = request.url.split("http://testserver/")

    assert url_redirect[0] == "/gestao/detalhar/municipio/{}".format(
        sistema_cultura.id
    )
    assert request.status_code == 302


def test_arquivo_enviado_pelo_componente(url, client, plano_trabalho, login_staff):
    """ Testa se o arquivo enviado pelo componente está correto """

    conselho = mommy.make("Componente", tipo=3, situacao=1)
    sistema_cultura = mommy.make("SistemaCultura", _fill_optional=['ente_federado',
        'cadastrador'], conselho=conselho)

    arquivo = SimpleUploadedFile("conselho.txt", b"file_content", content_type="text/plain")
    conselho.arquivo = arquivo
    conselho.save()

    request = client.get(
        url.format(id=sistema_cultura.id, componente="conselho", resultado="0")
    )

    assert request.context["arquivo"] == conselho.arquivo


def test_arquivo_enviado_salvo_no_diretorio_do_componente(
    url, client, plano_trabalho, login
):
    """ Testa se o arquivo enviando pelo componente está sendo salvo no
    diretório especifico dentro da pasta do ente federado."""

    arquivo = plano_trabalho.fundo_cultura.arquivo

    assert arquivo.url == "/media/{id}/docs/{componente}/{arquivo}".format(
        id=login.municipio.id,
        componente=plano_trabalho.fundo_cultura._meta.object_name.lower(),
        arquivo=plano_trabalho.fundo_cultura.arquivo.name.split("/")[3],
    )


def test_exibicao_historico_diligencia(url, client, plano_trabalho, login_staff):
    """Testa se o histórico de diligências é retornado pelo contexto"""
    orgao_gestor = mommy.make("Componente", tipo=1, situacao=1)
    sistema_cultura = mommy.make("SistemaCultura", _fill_optional=['ente_federado',
        'cadastrador'], orgao_gestor=orgao_gestor)

    arquivo = SimpleUploadedFile("lei.txt", b"file_content", content_type="text/plain")
    orgao_gestor.arquivo = arquivo
    orgao_gestor.save()

    diligencia = mommy.make(
        "Diligencia", _quantity=4, componente=sistema_cultura.orgao_gestor
    )
    diligencias = (
        sistema_cultura.orgao_gestor.diligencias.all()
        .order_by("-data_criacao")
        .order_by("-id")[:3]
    )

    request = client.get(
        url.format(id=sistema_cultura.id, componente="orgao_gestor", resultado="0")
    )
    diferenca_listas = set(diligencias).symmetric_difference(
        set(request.context["historico_diligencias"])
    )
    assert diferenca_listas == set()


def test_captura_nome_usuario_logado_na_diligencia(
    url, client, plano_trabalho, login_staff
):
    """
        Testa se o nome do usuario logado é capturado assim que uma diligencia for feita
    """
    orgao_gestor = mommy.make("Componente", tipo=1, situacao=1)
    sistema_cultura = mommy.make("SistemaCultura", _fill_optional=['ente_federado',
        'cadastrador'], orgao_gestor=orgao_gestor)

    arquivo = SimpleUploadedFile("lei.txt", b"file_content", content_type="text/plain")
    orgao_gestor.arquivo = arquivo
    orgao_gestor.save()

    request = client.post(
        url.format(id=sistema_cultura.id, componente="orgao_gestor", resultado="0"),
        data={"classificacao_arquivo": "4", "texto_diligencia": "Muito legal"},
    )

    diligencia = DiligenciaSimples.objects.last()

    assert diligencia.usuario == login_staff

@pytest.mark.skip("Necessita implementar a tela de atualização da situação")
def test_muda_situacao_arquivo_componente(url, client, login_staff):
    """ Testa se ao realizar o post da diligência a situação do arquivo do componente é alterada """
    orgao_gestor = mommy.make("Componente", tipo=1, situacao=1)
    sistema_cultura = mommy.make("SistemaCultura", _fill_optional=['ente_federado',
        'cadastrador'], orgao_gestor=orgao_gestor)

    arquivo = SimpleUploadedFile("lei.txt", b"file_content", content_type="text/plain")
    orgao_gestor.arquivo = arquivo
    orgao_gestor.save()

    url = f"/gestor/{sistema_cultura.id}/diligencia/orgao_gestor/{orgao_gestor.id}/situacao"

    request = client.post(url,
        data={"situacao": 4},
    )

    import ipdb; ipdb.set_trace()
    assert SistemaCultura.objects.last().orgao_gestor.situacao == 4

    orgao_gestor.delete()
    sistema_cultura.delete()


def test_insere_link_publicacao_dou(client, plano_trabalho, login_staff):
    """ Testa se ao inserir o link da publicacao no dou o objeto usuario é alterado """

    user = plano_trabalho.usuario

    url = reverse('gestao:alterar_dados_adesao', kwargs={'pk': user.id})

    client.post(url, data={'estado_processo': '6', 'data_publicacao_acordo': '28/06/2018',
        'link_publicacao_acordo': 'https://www.google.com/'})

    user.refresh_from_db()
    assert user.link_publicacao_acordo == "https://www.google.com/"


def test_insere_sei(client, plano_trabalho, login_staff):
    """ Testa se ao inserir sei o objeto usuario é alterado """

    user = plano_trabalho.usuario

    url = reverse('gestao:alterar_dados_adesao', kwargs={'pk': user.id})

    client.post(url, data={'processo_sei': '123456'})

    user.refresh_from_db()

    assert user.processo_sei == "123456"


def test_retorno_200_para_detalhar_municipio(client, plano_trabalho, login_staff):
    """ Testa se página de detalhamento do município retorna 200 """

    sistema_cultura = mommy.make("SistemaCultura")
    request = client.get("/gestao/detalhar/municipio/{}".format(sistema_cultura.id))
    assert request.status_code == 200


@pytest.mark.skip
def test_retorno_do_form_da_diligencia(url, client, login_staff):
    """ Testa se form retornado no contexto tem as opções corretas dependendo do tipo de resultado"""

    SITUACOES = (
        (0, "Em preenchimento"),
        (1, "Avaliando anexo"),
        (2, "Concluída"),
        (3, "Arquivo aprovado com ressalvas"),
        (4, "Arquivo danificado"),
        (5, "Arquivo incompleto"),
        (6, "Arquivo incorreto")
    )

    orgao_gestor = mommy.make("Componente", tipo=1, situacao=1)
    sistema_cultura = mommy.make("SistemaCultura", _fill_optional=['ente_federado',
        'cadastrador'], orgao_gestor=orgao_gestor)

    arquivo = SimpleUploadedFile("lei.txt", b"file_content", content_type="text/plain")
    orgao_gestor.arquivo = arquivo
    orgao_gestor.save()

    request_aprova = client.get(
        url.format(id=sistema_cultura.id, componente="orgao_gestor", resultado=1)
    )
    request_recusa = client.get(
        url.format(id=sistema_cultura.id, componente="orgao_gestor", resultado=0)
    )

    classificacao_aprova = set(
        request_aprova.context["form"].fields["classificacao_arquivo"].choices
    )
    classificacao_recusa = set(
        request_recusa.context["form"].fields["classificacao_arquivo"].choices
    )

    assert (
        classificacao_aprova.symmetric_difference(SITUACOES[2:3])
        == set()
    )
    assert (
        classificacao_recusa.symmetric_difference(SITUACOES[4:7])
        == set()
    )


def usuario_id_retornado_pelo_context_diligencia(
    url, client, plano_trabalho, login_staff
):
    """ Testa se o id do usuário enviado pelo context está correto """

    request = client.get(
        url.format(id=plano_trabalho.id, componente="orgao_gestor", resultado="0")
    )

    assert request.context["usuario_id"] == plano_trabalho.usuario.id


def test_criacao_diligencia_exclusiva_para_gestor(client, url, plano_trabalho, login):
    """Testa se ao tentar acessar a url de criação da diligência o usuário
    que não é autorizado é redirecionado para a tela de login"""

    url_diligencia = url.format(
        id=plano_trabalho.id, componente="orgao_gestor", resultado="1"
    )

    request = client.get(url_diligencia)

    url_redirect = request.url.split("http://testserver/")
    url_login = "/admin/login/?next={}".format(url_diligencia)

    assert request.status_code == 302
    assert url_redirect[0] == url_login


def test_listar_documentos(client, plano_trabalho, login_staff):
    """ Testa funcionalidade de listagem de entes federados para alterar seus documentos 
    na tela de gestão """

    templates = ["listar_sistemas", "listar_orgaos", "listar_fundos", "listar_conselhos"]

    for template in templates:

        url = reverse("gestao:listar_documentos", kwargs={"template": template})
        response = client.get(url)

        for usuario in response.context_data['object_list']:
            assert usuario.estado_processo == 6
            assert usuario.plano_trabalho != None


def test_alterar_documentos_orgao_gestor(client, plano_trabalho, login_staff):
    """ Testa se funcionalidade de alterar documento para orgão gestor na
    tela de gestão salva no field arquivo """

    arquivo = SimpleUploadedFile(
        "orgao.txt", b"file_content", content_type="text/plain"
    )

    url = reverse("gestao:alterar_orgao", kwargs={"pk": plano_trabalho.orgao_gestor.id})

    client.post(url, data={"arquivo": arquivo, "data_publicacao": "28/06/2018"})

    name = OrgaoGestor.objects.first().arquivo.name.split("orgaogestor/")[1]
    situacao = OrgaoGestor.objects.first().situacao

    assert name == arquivo.name
    assert situacao.id == 1


def test_inserir_documentos_orgao_gestor(client, plano_trabalho, login_staff):
    """ Testa se funcionalidade de inserir documento para orgão gestor na
    tela de gestão salva no field arquivo """

    arquivo = SimpleUploadedFile(
        "orgao.txt", b"file_content", content_type="text/plain"
    )

    url = reverse("gestao:inserir_orgao", kwargs={"pk": plano_trabalho.id})

    client.post(url, data={"arquivo": arquivo, "data_publicacao": "28/06/2018"})

    name = OrgaoGestor.objects.last().arquivo.name.split("orgaogestor/")[1]
    situacao = OrgaoGestor.objects.last().situacao

    assert name == arquivo.name
    assert situacao.id == 1


def test_alterar_documentos_criacao_sistema(client, plano_trabalho, login_staff):
    """ Testa se funcionalidade de alterar documento para sistema de cultura na
    tela de gestão salva no field arquivo """

    arquivo = SimpleUploadedFile(
        "sistema_cultura.txt", b"file_content", content_type="text/plain"
    )

    url = reverse(
        "gestao:alterar_sistema", kwargs={"pk": plano_trabalho.criacao_sistema.id}
    )

    client.post(url, data={"arquivo": arquivo, "data_publicacao": "28/06/2018"})

    name = CriacaoSistema.objects.first().arquivo.name.split("criacaosistema/")[1]
    situacao = CriacaoSistema.objects.first().situacao

    assert name == arquivo.name
    assert situacao.id == 1


def test_inserir_documentos_criacao_sistema(client, plano_trabalho, login_staff):
    """ Testa se funcionalidade de inserir documento para sistema de cultura na
    tela de gestão salva no field arquivo """

    arquivo = SimpleUploadedFile(
        "sistema_cultura.txt", b"file_content", content_type="text/plain"
    )

    url = reverse(
        "gestao:inserir_sistema", kwargs={"pk": plano_trabalho.id}
    )

    client.post(url, data={"arquivo": arquivo, "data_publicacao": "28/06/2018"})

    name = CriacaoSistema.objects.last().arquivo.name.split("criacaosistema/")[1]
    situacao = CriacaoSistema.objects.last().situacao

    assert name == arquivo.name
    assert situacao.id == 1


def test_inserir_documentos_fundo_cultura(client, plano_trabalho, login_staff):
    """ Testa se funcionalidade de inserir documento para o fundo de cultura na
    tela de gestão salva no field arquivo """

    arquivo = SimpleUploadedFile(
        "fundo_cultura.txt", b"file_content", content_type="text/plain"
    )

    url = reverse(
        "gestao:alterar_fundo", kwargs={"pk": plano_trabalho.fundo_cultura.id}
    )

    client.post(url, data={"arquivo": arquivo, "data_publicacao": "28/06/2018"})

    name = FundoCultura.objects.last().arquivo.name.split("fundocultura/")[1]
    situacao = FundoCultura.objects.last().situacao

    assert name == arquivo.name
    assert situacao.id == 1


def test_alterar_documentos_fundo_cultura(client, plano_trabalho, login_staff):
    """ Testa se funcionalidade de alterar documento para o fundo de cultura na
    tela de gestão salva no field arquivo """

    arquivo = SimpleUploadedFile(
        "fundo_cultura.txt", b"file_content", content_type="text/plain"
    )

    url = reverse(
        "gestao:alterar_fundo", kwargs={"pk": plano_trabalho.fundo_cultura.id}
    )

    client.post(url, data={"arquivo": arquivo,  "data_publicacao": "28/06/2018"})

    name = FundoCultura.objects.first().arquivo.name.split("fundocultura/")[1]
    situacao = FundoCultura.objects.first().situacao

    assert name == arquivo.name
    assert situacao.id == 1


def test_inserir_documentos_plano_cultura(client, plano_trabalho, login_staff):
    """ Testa se funcionalidade de inserir documento para plano de cultura na
    tela de gestão salva no field arquivo """

    arquivo = SimpleUploadedFile(
        "plano_cultura.txt", b"file_content", content_type="text/plain"
    )

    url = reverse(
        "gestao:alterar_plano", kwargs={"pk": plano_trabalho.plano_cultura.id}
    )

    client.post(url, data={"arquivo": arquivo, "data_publicacao": "28/06/2018"})

    name = PlanoCultura.objects.last().arquivo.name.split("planocultura/")[1]
    situacao = PlanoCultura.objects.last().situacao

    assert name == arquivo.name
    assert situacao.id == 1


def test_alterar_documentos_plano_cultura(client, plano_trabalho, login_staff):
    """ Testa se funcionalidade de alterar documento para plano de cultura na
    tela de gestão salva no field arquivo """

    arquivo = SimpleUploadedFile(
        "plano_cultura.txt", b"file_content", content_type="text/plain"
    )

    url = reverse(
        "gestao:alterar_plano", kwargs={"pk": plano_trabalho.plano_cultura.id}
    )

    client.post(url, data={"arquivo": arquivo, "data_publicacao": "28/06/2018"})

    name = PlanoCultura.objects.first().arquivo.name.split("planocultura/")[1]
    situacao = PlanoCultura.objects.first().situacao

    assert name == arquivo.name
    assert situacao.id == 1


def test_alterar_documentos_conselho_cultural(client, plano_trabalho, login_staff):
    """ Testa se funcionalidade de alterar documento para conselho cultural na
    tela de gestão salva no field arquivo """

    arquivo = SimpleUploadedFile(
        "conselho_cultural.txt", b"file_content", content_type="text/plain"
    )

    url = reverse(
        "gestao:alterar_conselho", kwargs={"pk": plano_trabalho.conselho_cultural.id}
    )

    client.post(url, data={"arquivo": arquivo, "data_publicacao": "28/06/2018"})

    name = ConselhoCultural.objects.first().arquivo.name.split("conselhocultural/")[1]
    situacao = ConselhoCultural.objects.first().situacao

    assert name == arquivo.name
    assert situacao.id == 1


def test_inserir_documentos_conselho_cultural(client, plano_trabalho, login_staff):
    """ Testa se funcionalidade de inserção documentos para conselho cultural na
    tela de gestão salva no field arquivo """

    arquivo = SimpleUploadedFile(
        "conselho_cultural.txt", b"file_content", content_type="text/plain"
    )

    url = reverse(
        "gestao:inserir_conselho", kwargs={"pk": plano_trabalho.id}
    )

    client.post(url, data={"arquivo": arquivo, "data_publicacao": "28/06/2018"})

    name = ConselhoCultural.objects.last().arquivo.name.split("conselhocultural/")[1]
    situacao = ConselhoCultural.objects.last().situacao

    assert name == arquivo.name
    assert situacao.id == 1


def test_retorna_200_para_diligencia_geral(client, url, login_staff):
    """ Testa se retonar 200 ao dar um get na diligencia geral """
    diligencia = mommy.make("DiligenciaSimples")
    sistema_cultura = mommy.make("SistemaCultura", _fill_optional=['ente_federado',
        'cadastrador'], diligencia=diligencia)

    url = f"/gestao/{sistema_cultura.id}/diligencia"
    request = client.get(url)

    assert request.status_code == 200


def test_salvar_informacoes_no_banco_diligencia_geral(
    url, client, login_staff
):
    """Testa se as informacoes validadas pelo form estao sendo salvas no banco"""
    sistema_cultura = mommy.make("SistemaCultura", _fill_optional=['ente_federado',
        'cadastrador'])

    url = reverse('gestao:diligencia_geral_adicionar', kwargs={"pk": sistema_cultura.id})

    response = client.post(url, data={"texto_diligencia": "bla"})

    diligencia = DiligenciaSimples.objects.first()

    assert DiligenciaSimples.objects.count() == 1
    assert DiligenciaSimples.objects.first() == sistema_cultura.diligencia_simples


def test_redirecionamento_de_pagina_apos_POST_diligencia_geral(
    url, client, login_staff
):
    """ Testa se há o redirecionamento de página após o POST da diligência """
    sistema_cultura = mommy.make("SistemaCultura", _fill_optional=['ente_federado',
        'cadastrador'])

    url = reverse('gestao:diligencia_geral_adicionar', kwargs={"pk": sistema_cultura.id})
    request = client.post(url, data={"classificacao_arquivo": "4", "texto_diligencia": "Ta errado cara"})
    url_redirect = request.url.split("http://testserver/")

    diligencia = DiligenciaSimples.objects.first()

    assert url_redirect[0] == reverse("gestao:diligencia_geral", kwargs={"pk": diligencia.id})
    assert request.status_code == 302


def test_situacoes_componentes_diligencia(url, client, plano_trabalho, login_staff):
    """ Testa as informações referentes aos componentes do
    plano de trabalho na diligência geral """
    legislacao = mommy.make("Componente", tipo=0, situacao=1, _create_files=True)
    orgao = mommy.make("Componente", tipo=1, situacao=2, _create_files=True)
    fundo = mommy.make("Componente", tipo=2, situacao=3, _create_files=True)
    conselho = mommy.make("Componente", tipo=3, situacao=4, _create_files=True)
    plano = mommy.make("Componente", tipo=4, situacao=5, _create_files=True)

    sistema_cultura = mommy.make("SistemaCultura", _fill_optional=['ente_federado',
        'cadastrador'], legislacao=legislacao, orgao_gestor=orgao, 
        fundo_cultura=fundo, conselho=conselho, plano=plano)

    url = f"/gestao/{sistema_cultura.id}/diligencia"
    response = client.get(url)

    situacoes = response.context["situacoes"]

    # import ipdb; ipdb.set_trace()
    assert situacoes["legislacao"] == sistema_cultura.legislacao.get_situacao_display()
    assert situacoes["orgao_gestor"] == sistema_cultura.orgao_gestor.get_situacao_display()
    assert situacoes["fundo_cultura"] == sistema_cultura.fundo_cultura.get_situacao_display()
    assert situacoes["conselho"] == sistema_cultura.conselho.get_situacao_display()
    assert situacoes["plano"] == sistema_cultura.plano.get_situacao_display()


def test_tipo_diligencia_componente(url, client, plano_trabalho, login_staff):
    """ Testa criação da diligência específica de um componente"""
    orgao_gestor = mommy.make("Componente", tipo=1, situacao=1)
    sistema_cultura = mommy.make("SistemaCultura", _fill_optional=['ente_federado',
        'cadastrador'], orgao_gestor=orgao_gestor)

    arquivo = SimpleUploadedFile("lei.txt", b"file_content", content_type="text/plain")
    orgao_gestor.arquivo = arquivo
    orgao_gestor.save()

    request = client.post(
        url.format(id=sistema_cultura.id, componente="orgao_gestor", resultado="0"),
        data={"classificacao_arquivo": "4", "texto_diligencia": "Ta errado cara"},
    )

    sistema_cultura.orgao_gestor.refresh_from_db()

    assert DiligenciaSimples.objects.count() == 1
    assert DiligenciaSimples.objects.first() == sistema_cultura.orgao_gestor.diligencia


def test_envio_email_diligencia_geral(client, login_staff):
    """ Testa envio do email para diligência geral """
    sistema_cultura = mommy.make("SistemaCultura", _fill_optional=['ente_federado',
        'cadastrador'])

    url = "/gestao/{id}/diligencia/"

    sistema_cultura.cadastrador.user.email="teste@teste.com"
    sistema_cultura.cadastrador.user.save()

    request = client.post(
        url.format(id=sistema_cultura.id),
        data={"texto_diligencia": "Ta errado cara"},
    )

    assert len(mail.outbox) == 1


def test_diligencia_geral_sem_componentes(url, client, plano_trabalho, login_staff):
    """ Testa se ao fazer a diligência geral de um ente federado
    sem componentes retorne componente inexistente"""

    sistema_cultura = mommy.make("SistemaCultura", legislacao=None, orgao_gestor=None,
        plano=None, conselho=None, fundo_cultura=None, _fill_optional=['ente_federado',
        'cadastrador'])

    url = reverse('gestao:diligencia_geral_adicionar', kwargs={"pk": sistema_cultura.id})

    request = client.get(url)

    for situacao in request.context['situacoes'].values():
        assert situacao == 'Inexistente'


def test_filtro_cidades_por_uf(client):
    """ Testa se CidadeChain está retornando os municipios quando uma UF
    é informada
    """

    Uf.objects.all().delete()
    mg = mommy.make("Uf", sigla="MG")
    sp = mommy.make("Uf", sigla="SP")
    mommy.make("Cidade", uf=mg, _quantity=3)
    mommy.make("Cidade", uf=sp, _quantity=2)

    url = "{url}?q={sigla}".format(url=reverse("gestao:cidade_chain"), sigla="MG")

    request = client.get(url)
    assert len(request.json()["results"]) == 3


def test_filtro_cidades_por_uf_pk(client):
    """ Testa se CidadeChain está retornando os municipios quando a pk de uma UF
    é informada
    """

    Uf.objects.all().delete()
    mg = mommy.make("Uf", sigla="MG")
    sp = mommy.make("Uf", sigla="SP")
    mommy.make("Cidade", uf=mg, _quantity=3)
    mommy.make("Cidade", uf=sp, _quantity=2)

    q = json.dumps({'estado': mg.pk})
    url = "{url}?forward={q}".format(url=reverse("gestao:cidade_chain"), q=q)
    request = client.get(url)
    assert len(request.json()["results"]) == 3


def test_filtra_ufs_por_sigla(client):
    """ Testa se UfChain retorna a UF correta ao passar a sigla """

    Uf.objects.all().delete()
    mg = mommy.make("Uf", sigla="MG", nome_uf="Minas Gerais")
    mommy.make("Uf", sigla="PA", nome_uf="Pará")
    mommy.make("Uf", sigla="BA", nome_uf="Bahia")

    url = "{url}?q={param}".format(url=reverse("gestao:uf_chain"), param=mg.sigla)

    request = client.get(url)

    assert len(request.json()["results"]) == 1
    assert request.json()["results"][0]['text'] == mg.sigla


def test_filtra_ufs_por_nome(client):
    """ Testa se UfChain retorna a UF correta ao passar o nome"""

    Uf.objects.all().delete()
    mg = mommy.make("Uf", sigla="MG", nome_uf="Minas Gerais")
    mommy.make("Uf", _quantity=10)

    url = "{url}?q={param}".format(url=reverse("gestao:uf_chain"), param="Minas")
    request = client.get(url)

    assert len(request.json()["results"]) == 1
    assert request.json()["results"][0]['text'] == mg.sigla


def test_acompanhar_adesao_ordenar_data_um_componente_por_plano(client, login_staff):
    """ Testa ordenação da página de acompanhamento das adesões
    por data de envio mais antiga entre os componentes"""

    user_sem_analise_recente = mommy.make('Usuario', _fill_optional=['plano_trabalho', 'municipio'])
    user_sem_analise_recente.plano_trabalho.criacao_sistema = mommy.make('CriacaoSistema')
    user_sem_analise_recente.plano_trabalho.save()
    user_sem_analise_recente.plano_trabalho.criacao_sistema.situacao = SituacoesArquivoPlano.objects.get(pk=1)
    user_sem_analise_recente.plano_trabalho.criacao_sistema.data_envio = datetime.date(2018, 1, 1)
    user_sem_analise_recente.plano_trabalho.criacao_sistema.save()

    user_sem_analise_antigo = mommy.make('Usuario', _fill_optional=['plano_trabalho', 'municipio'])
    user_sem_analise_antigo.plano_trabalho.orgao_gestor = mommy.make('OrgaoGestor')
    user_sem_analise_antigo.plano_trabalho.save()
    user_sem_analise_antigo.plano_trabalho.orgao_gestor.situacao = SituacoesArquivoPlano.objects.get(pk=1)
    user_sem_analise_antigo.plano_trabalho.orgao_gestor.data_envio = datetime.date(2017, 1, 1)
    user_sem_analise_antigo.plano_trabalho.orgao_gestor.save()

    user_com_diligencia_antigo = mommy.make('Usuario', _fill_optional=['plano_trabalho', 'municipio'])
    user_com_diligencia_antigo.plano_trabalho.fundo_cultura = mommy.make('FundoCultura')
    user_com_diligencia_antigo.plano_trabalho.save()
    user_com_diligencia_antigo.plano_trabalho.fundo_cultura.situacao = SituacoesArquivoPlano.objects.get(pk=4)
    user_com_diligencia_antigo.plano_trabalho.fundo_cultura.data_envio = datetime.date(2016, 1, 1)
    user_com_diligencia_antigo.plano_trabalho.fundo_cultura.save()

    user_com_analise_antigo = mommy.make('Usuario', _fill_optional=['plano_trabalho', 'municipio'])
    user_com_analise_antigo.plano_trabalho.fundo_cultura = mommy.make('FundoCultura')
    user_com_analise_antigo.plano_trabalho.save()
    user_com_analise_antigo.plano_trabalho.fundo_cultura.situacao = SituacoesArquivoPlano.objects.get(pk=2)
    user_com_analise_antigo.plano_trabalho.fundo_cultura.data_envio = datetime.date(2016, 1, 1)
    user_com_analise_antigo.plano_trabalho.fundo_cultura.save()

    url = reverse('gestao:acompanhar_adesao')
    response = client.get(url)

    assert response.context_data['object_list'][0] == user_sem_analise_antigo.municipio
    assert response.context_data['object_list'][1] == user_sem_analise_recente.municipio
    assert response.context_data['object_list'][2] == user_com_diligencia_antigo.municipio
    assert response.context_data['object_list'][3] == user_com_analise_antigo.municipio


def test_acompanhar_adesao_ordenar_data_com_plano_com_mais_de_um_componente(client, login_staff):
    """ Testa se na página de acompanhamento de adesões, quando há planos com múltiplos 
    componentes, o correto é considerado para ordenação pela data """

    user_plano_1 = mommy.make('Usuario', _fill_optional=['plano_trabalho', 'municipio'])
    user_plano_1.plano_trabalho.criacao_sistema = mommy.make('CriacaoSistema')
    user_plano_1.plano_trabalho.save()
    user_plano_1.plano_trabalho.criacao_sistema.situacao = SituacoesArquivoPlano.objects.get(pk=5)
    user_plano_1.plano_trabalho.criacao_sistema.data_envio = datetime.date(2016, 1, 1)
    user_plano_1.plano_trabalho.criacao_sistema.save()

    user_plano_1.plano_trabalho.orgao_gestor = mommy.make('OrgaoGestor')
    user_plano_1.plano_trabalho.save()
    user_plano_1.plano_trabalho.orgao_gestor.situacao = SituacoesArquivoPlano.objects.get(pk=1)
    user_plano_1.plano_trabalho.orgao_gestor.data_envio = datetime.date(2017, 1, 1)
    user_plano_1.plano_trabalho.orgao_gestor.save()

    user_plano_2 = mommy.make('Usuario', _fill_optional=['plano_trabalho', 'municipio'])
    user_plano_2.plano_trabalho.fundo_cultura = mommy.make('FundoCultura')
    user_plano_2.plano_trabalho.save()
    user_plano_2.plano_trabalho.fundo_cultura.situacao = SituacoesArquivoPlano.objects.get(pk=4)
    user_plano_2.plano_trabalho.fundo_cultura.data_envio = datetime.date(2017, 1, 1)
    user_plano_2.plano_trabalho.fundo_cultura.save()

    user_plano_2.plano_trabalho.plano_cultura = mommy.make('PlanoCultura')
    user_plano_2.plano_trabalho.save()
    user_plano_2.plano_trabalho.plano_cultura.situacao = SituacoesArquivoPlano.objects.get(pk=3)
    user_plano_2.plano_trabalho.plano_cultura.data_envio = datetime.date(2018, 1, 1)
    user_plano_2.plano_trabalho.plano_cultura.save()

    user_plano_3 = mommy.make('Usuario', _fill_optional=['plano_trabalho', 'municipio'])
    user_plano_3.plano_trabalho.conselho_cultural = mommy.make('ConselhoCultural')
    user_plano_3.plano_trabalho.save()
    user_plano_3.plano_trabalho.conselho_cultural.situacao = SituacoesArquivoPlano.objects.get(pk=1)
    user_plano_3.plano_trabalho.conselho_cultural.data_envio = datetime.date(2018, 1, 1)
    user_plano_3.plano_trabalho.conselho_cultural.save()

    url = reverse('gestao:acompanhar_adesao')
    response = client.get(url)

    assert len(response.context_data['object_list']) == 3
    assert response.context_data['object_list'][0] == user_plano_1.municipio
    assert response.context_data['object_list'][1] == user_plano_3.municipio
    assert response.context_data['object_list'][2] == user_plano_2.municipio


def test_acompanhar_adesao_ordenar_estado_processo(client, plano_trabalho, login_staff):
    """ Testa ordenação da página de acompanhamento das adesões
    por data de envio mais antiga entre os componentes e
    estado do processo da adesão """

    user = mommy.make('Usuario', estado_processo=1,
                      _fill_optional=['plano_trabalho', 'municipio'])
    user.plano_trabalho.criacao_sistema = mommy.make(
            'CriacaoSistema', situacao_id=1, data_envio=datetime.date(2018, 1, 1))
    user.plano_trabalho.save()

    ente_federado_publicado = plano_trabalho.usuario.municipio
    ente_federado_publicado.usuario.estado_processo = 6
    ente_federado_publicado.usuario.save()

    ente_sem_cadastrador = mommy.make('Municipio')

    url = reverse('gestao:acompanhar_adesao')
    response = client.get(url)

    assert response.context_data['object_list'][0] == ente_federado_publicado
    assert response.context_data['object_list'][1] == user.municipio
    assert response.context_data['object_list'][2] == ente_sem_cadastrador


def test_alterar_dados_adesao_detalhe_municipio(client, login_staff):
    """ Testa alterar os dados da adesão na tela de detalhe do município """

    usuario = mommy.make('Usuario', _fill_optional=['municipio'])
    url = reverse('gestao:alterar_dados_adesao', kwargs={'pk': usuario.id})
    data = {'estado_processo': 6, 'data_publicacao_acordo': datetime.date.today(), 'processo_sei': '123456765'}
    response = client.post(url, data=data)

    usuario.refresh_from_db()

    assert response.status_code == 302
    assert usuario.estado_processo == '6'
    assert usuario.data_publicacao_acordo == datetime.date.today()
    assert usuario.processo_sei == '123456765'


def test_alterar_dados_adesao_detalhe_municipio_sem_valores(client, login_staff):
    """ Testa retorno ao tentar alterar os dados da adesão sem passar dados válidos """

    usuario = mommy.make('Usuario', _fill_optional=['municipio'])
    url = reverse('gestao:alterar_dados_adesao', kwargs={'pk': usuario.id})
    data = {}

    response = client.post(url, data=data)

    usuario.refresh_from_db()

    assert response.status_code == 302
    assert usuario.estado_processo == '0'
    assert not usuario.data_publicacao_acordo
    assert not usuario.processo_sei


def test_alterar_cadastrador_municipio(client, login_staff):
    """ Testa alteração de cadastrador de um ente federal municipal """

    municipio = mommy.make('Municipio', _fill_optional=['cidade'])
    mommy.make('Usuario', municipio=municipio)
    new_user = mommy.make('Usuario', user__username='34701068004')
    url = reverse('gestao:alterar_cadastrador')

    data = {
        'cpf_usuario': new_user.user.username,
        'municipio': municipio.cidade.id,
        'estado': municipio.estado.codigo_ibge
    }

    client.post(url, data=data)

    municipio.refresh_from_db()

    assert municipio.usuario == new_user


def test_alterar_cadastrador_estado(client, login_staff):
    """ Testa alteração de cadastrador de um ente federal estadual"""

    municipio = mommy.make('Municipio')
    mommy.make('Usuario', municipio=municipio)
    new_user = mommy.make('Usuario', user__username='34701068004')
    url = reverse('gestao:alterar_cadastrador')

    data = {
        'cpf_usuario': new_user.user.username,
        'estado': municipio.estado.codigo_ibge
    }

    client.post(url, data=data)

    municipio.refresh_from_db()

    assert municipio.usuario == new_user


def test_ajax_cadastrador_cpf_ente_existente_muncipal(client, login_staff,
                                                      plano_trabalho):
    """ Testa retorno de CPF do cadastrador de um ente federado municipal
    existente no sistema """
    municipio = plano_trabalho.usuario.municipio
    usuario = plano_trabalho.usuario

    url = reverse('gestao:ajax_cadastrador_cpf')
    url = url + '?municipio={}&estado={}'.format(municipio.cidade.id,
                                                 municipio.estado.codigo_ibge)
    client.login(username=login_staff.user.username, password='123456')

    response = client.get(url)

    assert response.status_code == 200
    assert response.json()['data_publicacao_acordo'] == str(usuario.data_publicacao_acordo)
    assert response.json()['cpf'] == usuario.user.username


def test_ajax_cadastrador_cpf_ente_existente_estadual(client, login_staff,
                                                      plano_trabalho):
    """ Testa retorno de CPF do cadastrador de um ente federado estadual
    existente no sistema """
    municipio = mommy.make('Municipio')
    usuario = mommy.make('Usuario', municipio=municipio,
                         _fill_optional=['data_publicacao_acordo'])

    url = reverse('gestao:ajax_cadastrador_cpf')
    url = url + '?estado={}'.format(municipio.estado.codigo_ibge)
    client.login(username=login_staff.user.username, password='123456')

    response = client.get(url)

    assert response.status_code == 200
    assert response.json()['data_publicacao_acordo'] == str(usuario.data_publicacao_acordo)
    assert response.json()['cpf'] == usuario.user.username


def test_ajax_cadastrador_ente_inexistente(client, login_staff):
    """ Testa retorno ao passar um ente federado não existente """

    url = reverse('gestao:ajax_cadastrador_cpf') + '?estado=&municipio=0'

    client.login(username=login_staff.user.username, password='123456')

    response = client.get(url)

    assert response.status_code == 400

