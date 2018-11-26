import datetime
import json
import pytest

from django.urls import resolve
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core import mail

from model_mommy import mommy

from gestao.models import DiligenciaSimples
from gestao.forms import DiligenciaForm
from adesao.models import Uf
from adesao.models import SistemaCultura

from planotrabalho.models import OrgaoGestor
from planotrabalho.models import CriacaoSistema
from planotrabalho.models import FundoCultura
from planotrabalho.models import PlanoCultura
from planotrabalho.models import ConselhoCultural
from planotrabalho.models import SituacoesArquivoPlano
from planotrabalho.models import Componente


pytestmark = pytest.mark.django_db


@pytest.fixture
def url():
    """Retorna uma string contendo a URL preparada para ser formatada."""

    return "/gestao/{id}/diligencia/{componente}"


def test_url_diligencia_retorna_200(url, client, login_staff):
    """
    Testa se há url referente à página de diligências.
    A url teria o formato: gestao/id_sistema_cultura/diligencia/componente_plano_trabalho
    """
    orgao_gestor = mommy.make("Componente", tipo=1, situacao=1)
    sistema_cultura = mommy.make(
        "SistemaCultura",
        ente_federado__cod_ibge=123456,
        _fill_optional='cadastrador',
        orgao_gestor=orgao_gestor,
    )

    arquivo = SimpleUploadedFile("lei.txt", b"file_content", content_type="text/plain")
    orgao_gestor.arquivo = arquivo
    orgao_gestor.save()

    request = client.get(
        url.format(id=sistema_cultura.pk, componente="orgao_gestor")
    )

    assert request.status_code == 200


def test_resolve_url_atraves_sua_view_name(url, client, plano_trabalho):
    """Testa se o Django retorna a url através da sua view_name"""

    resolved = resolve(
        url.format(id=plano_trabalho.id, componente="plano_cultura")
    )

    assert resolved.url_name == "diligencia_componente"
    assert resolved.kwargs["pk"] == plano_trabalho.id


def test_recepcao_componente_na_url_diligencia(url, client, plano_trabalho):
    """Testa se a url esta recebendo o componente correspondente a diligencia que sera escrita"""

    resolved = resolve(
        url.format(id=plano_trabalho.id, componente="lei_sistema")
    )

    assert resolved.kwargs["componente"] == "lei_sistema"


def test_url_componente_retorna_200(url, client, login_staff):
    """Testa se a url retorna 200 ao acessar um componente"""

    orgao_gestor = mommy.make("Componente", tipo=1, situacao=1)
    sistema_cultura = mommy.make(
        "SistemaCultura",
        ente_federado__cod_ibge=123456,
        _fill_optional='cadastrador',
        orgao_gestor=orgao_gestor,
    )

    arquivo = SimpleUploadedFile("lei.txt", b"file_content", content_type="text/plain")
    orgao_gestor.arquivo = arquivo
    orgao_gestor.save()

    request = client.get(
        url.format(id=sistema_cultura.id, componente="orgao_gestor")
    )

    assert request.status_code == 200


def test_url_retorna_404_caso_componente_nao_exista(
    url, client, plano_trabalho, login_staff
):
    """Testa se a URL retorna 404 caso o componente não exista"""

    request = client.get(
        url.format(
            id=plano_trabalho.id, componente="um_componente_qualquer"
        )
    )

    assert request.status_code == 404


def test_renderiza_template(url, client, plano_trabalho, login_staff):
    """ Testa se o método da view renderiza um template"""

    request = client.get(
        url.format(id=plano_trabalho.id, componente="criacao_sistema")
    )
    assert request.content


def test_renderiza_template_diligencia(url, client, login_staff):
    """Testa se o template específico da diligência é renderizado corretamente"""

    conselho = mommy.make("Componente", tipo=3, situacao=1)
    sistema_cultura = mommy.make(
        "SistemaCultura",
        ente_federado__cod_ibge=123456,
        _fill_optional='cadastrador',
        conselho=conselho,
    )

    arquivo = SimpleUploadedFile(
        "conselho.txt", b"file_content", content_type="text/plain"
    )
    conselho.arquivo = arquivo
    conselho.save()

    request = client.get(
        url.format(id=sistema_cultura.id, componente="conselho")
    )
    assert "diligencia.html" == request.templates[0].name


def test_existencia_do_contexto_view(url, client, login_staff):
    """Testa se o contexto existe no retorno da view """

    contexts = ["sistema_cultura", "situacoes", "historico_diligencias"]

    sistema_cultura = mommy.make(
        "SistemaCultura", ente_federado__cod_ibge=123456, _fill_optional='cadastrador'
    )

    url = reverse(
        "gestao:diligencia_geral_adicionar", kwargs={"pk": sistema_cultura.id}
    )
    request = client.get(url)

    for context in contexts:
        assert context in request.context


def test_retorno_400_post_criacao_diligencia(url, client, login_staff):
    """ Testa se o status do retorno é 400 para requests sem os parâmetros esperados """

    orgao_gestor = mommy.make("Componente", tipo=1, situacao=1)
    sistema_cultura = mommy.make(
        "SistemaCultura",
        ente_federado__cod_ibge=123456,
        _fill_optional='cadastrador',
        orgao_gestor=orgao_gestor,
    )

    arquivo = SimpleUploadedFile("lei.txt", b"file_content", content_type="text/plain")
    orgao_gestor.arquivo = arquivo
    orgao_gestor.save()

    request = client.post(
        url.format(id=sistema_cultura.id, componente="orgao_gestor"),
        data={"cla": ""},
    )

    assert request.status_code == 400


def test_retorna_400_POST_classificacao_inexistente(url, client, login_staff):
    """
    Testa se o status do retorno é 400 quando feito um POST com a classificao invalida
    de um arquivo.
    """
    orgao_gestor = mommy.make("Componente", tipo=1, situacao=1)
    sistema_cultura = mommy.make(
        "SistemaCultura",
        ente_federado__cod_ibge=123456,
        _fill_optional='cadastrador',
        orgao_gestor=orgao_gestor,
    )

    arquivo = SimpleUploadedFile("lei.txt", b"file_content", content_type="text/plain")
    orgao_gestor.arquivo = arquivo
    orgao_gestor.save()

    request = client.post(
        url.format(id=sistema_cultura.id, componente="orgao_gestor"),
        data={"classificacao_arquivo": ""},
    )
    user = login_staff.user
    request.user = user

    assert request.status_code == 400


def test_tipo_do_form_utilizado_na_diligencia_view(url, client, login_staff):
    """ Testa se o form utilizado na diligencia_view é do tipo DiligenciaForm """

    orgao_gestor = mommy.make("Componente", tipo=1, situacao=1)
    sistema_cultura = mommy.make(
        "SistemaCultura",
        ente_federado__cod_ibge=123456,
        _fill_optional='cadastrador',
        orgao_gestor=orgao_gestor,
    )

    arquivo = SimpleUploadedFile("lei.txt", b"file_content", content_type="text/plain")
    orgao_gestor.arquivo = arquivo
    orgao_gestor.save()

    request = client.get(
        url.format(id=sistema_cultura.id, componente="orgao_gestor")
    )

    assert isinstance(request.context["form"], DiligenciaForm)


def test_invalido_form_para_post_diligencia(url, client, login_staff):
    """ Testa se o form invalida post com dados errados """

    orgao_gestor = mommy.make("Componente", tipo=1, situacao=1)
    sistema_cultura = mommy.make(
        "SistemaCultura",
        ente_federado__cod_ibge=123456,
        _fill_optional='cadastrador',
        orgao_gestor=orgao_gestor,
    )

    arquivo = SimpleUploadedFile("lei.txt", b"file_content", content_type="text/plain")
    orgao_gestor.arquivo = arquivo
    orgao_gestor.save()

    request = client.post(
        url.format(id=sistema_cultura.id, componente="orgao_gestor"),
        data={"classificacao_arquivo": "", "texto_diligencia": ""},
    )

    assert request.status_code == 400


def test_obj_ente_federado(url, client, login_staff):
    """ Testa se o objeto retornado ente_federado é uma String"""

    orgao_gestor = mommy.make("Componente", tipo=1, situacao=1)
    sistema_cultura = mommy.make(
        "SistemaCultura",
        ente_federado__cod_ibge=123456,
        _fill_optional='cadastrador',
        orgao_gestor=orgao_gestor,
    )

    arquivo = SimpleUploadedFile("lei.txt", b"file_content", content_type="text/plain")
    orgao_gestor.arquivo = arquivo
    orgao_gestor.save()

    request = client.get(
        url.format(id=sistema_cultura.id, componente="orgao_gestor")
    )

    assert isinstance(request.context["ente_federado"], str)
    assert request.context["ente_federado"] == sistema_cultura.ente_federado.nome


def test_404_para_plano_trabalho_invalido_diligencia(url, client, login_staff):
    """ Testa se a view da diligência retorna 404 para um plano de trabalho inválido """

    request = client.get(url.format(id="7", componente="orgao_gestor"))

    assert request.status_code == 404


def test_ente_federado_retornado_na_diligencia(url, client, login_staff):
    """
    Testa se ente_federado retornado está relacionado com o plano trabalho passado como parâmetro
    """

    conselho = mommy.make("Componente", tipo=3, situacao=1)
    sistema_cultura = mommy.make(
        "SistemaCultura",
        ente_federado__cod_ibge=123456,
        _fill_optional=["cadastrador"],
        conselho=conselho,
    )

    arquivo = SimpleUploadedFile(
        "conselho.txt", b"file_content", content_type="text/plain"
    )
    conselho.arquivo = arquivo
    conselho.save()

    request = client.get(
        url.format(id=sistema_cultura.id, componente="conselho")
    )

    assert request.context["ente_federado"] == sistema_cultura.ente_federado.nome


def test_salvar_informacoes_no_banco(url, client, login_staff):
    """Testa se as informacoes validadas pelo form estao sendo salvas no banco"""

    orgao_gestor = mommy.make("Componente", tipo=1, situacao=1)
    sistema_cultura = mommy.make(
        "SistemaCultura",
        ente_federado__cod_ibge=123456,
        _fill_optional='cadastrador',
        orgao_gestor=orgao_gestor,
    )

    arquivo = SimpleUploadedFile("lei.txt", b"file_content", content_type="text/plain")
    orgao_gestor.arquivo = arquivo
    orgao_gestor.save()

    response = client.post(
        url.format(id=sistema_cultura.id, componente="orgao_gestor"),
        data={"classificacao_arquivo": "4", "texto_diligencia": "bla"},
    )
    diligencia = DiligenciaSimples.objects.first()
    orgao_gestor.refresh_from_db()

    assert DiligenciaSimples.objects.count() == 1
    assert diligencia.texto_diligencia == "bla"
    assert diligencia.classificacao_arquivo == 4
    assert orgao_gestor.situacao == diligencia.classificacao_arquivo


def test_redirecionamento_de_pagina_apos_POST(url, client, login_staff):
    """ Testa se há o redirecionamento de página após o POST da diligência """

    orgao_gestor = mommy.make("Componente", tipo=1, situacao=1)
    sistema_cultura = mommy.make(
        "SistemaCultura",
        ente_federado__cod_ibge=123456,
        _fill_optional=["cadastrador"],
        orgao_gestor=orgao_gestor,
    )

    arquivo = SimpleUploadedFile("lei.txt", b"file_content", content_type="text/plain")
    orgao_gestor.arquivo = arquivo
    orgao_gestor.save()

    request = client.post(
        url.format(id=sistema_cultura.id, componente="orgao_gestor"),
        data={"classificacao_arquivo": "4", "texto_diligencia": "Ta errado cara"},
    )
    url_redirect = request.url.split("http://testserver/")

    assert url_redirect[0] == reverse(
        "gestao:detalhar", kwargs={"cod_ibge": sistema_cultura.ente_federado.cod_ibge}
    )
    assert request.status_code == 302


def test_arquivo_enviado_pelo_componente(url, client, login_staff):
    """ Testa se o arquivo enviado pelo componente está correto """

    conselho = mommy.make("Componente", tipo=3, situacao=1)
    sistema_cultura = mommy.make(
        "SistemaCultura",
        ente_federado__cod_ibge=123456,
        _fill_optional=["cadastrador"],
        conselho=conselho,
    )

    arquivo = SimpleUploadedFile(
        "conselho.txt", b"file_content", content_type="text/plain"
    )
    conselho.arquivo = arquivo
    conselho.save()

    request = client.get(
        url.format(id=sistema_cultura.id, componente="conselho")
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


def test_exibicao_historico_diligencia(url, client, login_staff):
    """Testa se o histórico de diligências é retornado pelo contexto"""
    sistema_cultura = mommy.make(
        "SistemaCultura", ente_federado__cod_ibge=123456, _fill_optional=["cadastrador"]
    )

    diligencias = mommy.make("DiligenciaSimples", _quantity=4)

    for diligencia in diligencias:
        diligencia.sistema_cultura.add(sistema_cultura)

    diligencias_ente = DiligenciaSimples.objects.filter(
        sistema_cultura__ente_federado__cod_ibge=sistema_cultura.ente_federado.cod_ibge)

    url = reverse(
        "gestao:diligencia_geral_adicionar", kwargs={"pk": sistema_cultura.id}
    )
    request = client.get(url)

    diferenca_listas = set(diligencias_ente).symmetric_difference(
        set(request.context["historico_diligencias"])
    )
    assert diferenca_listas == set()


def test_captura_nome_usuario_logado_na_diligencia(
    url, client, login_staff
):
    """
        Testa se o nome do usuario logado é capturado assim que uma diligencia for feita
    """
    orgao_gestor = mommy.make("Componente", tipo=1, situacao=1)
    sistema_cultura = mommy.make(
        "SistemaCultura",
        ente_federado__cod_ibge=123456,
        _fill_optional=["cadastrador"],
        orgao_gestor=orgao_gestor,
    )

    arquivo = SimpleUploadedFile("lei.txt", b"file_content", content_type="text/plain")
    orgao_gestor.arquivo = arquivo
    orgao_gestor.save()

    request = client.post(
        url.format(id=sistema_cultura.id, componente="orgao_gestor"),
        data={"classificacao_arquivo": "4", "texto_diligencia": "Muito legal"},
    )

    diligencia = DiligenciaSimples.objects.last()

    assert diligencia.usuario == login_staff


def test_insere_link_publicacao_dou(client, sistema_cultura, login_staff):
    """ Testa se ao inserir o link da publicacao no dou o objeto usuario é alterado """

    url = reverse("gestao:alterar_dados_adesao", kwargs={"cod_ibge": sistema_cultura.ente_federado.cod_ibge})

    client.post(
        url,
        data={
            "estado_processo": "6",
            "data_publicacao_acordo": "28/06/2018",
            "link_publicacao_acordo": "https://www.google.com/",
        },
    )

    sistema_atualizado = SistemaCultura.sistema.get(ente_federado__cod_ibge=sistema_cultura
        .ente_federado.cod_ibge)
    assert sistema_atualizado.link_publicacao_acordo == "https://www.google.com/"


def test_insere_sei(client, sistema_cultura, login_staff):
    """ Testa se ao inserir sei o sistema_cultura é alterado """

    url = reverse("gestao:alterar_dados_adesao", kwargs={"cod_ibge": sistema_cultura.ente_federado.cod_ibge})

    client.post(url, data={"estado_processo": "6", "processo_sei": "123456"})

    sistema_atualizado = SistemaCultura.sistema.get(ente_federado__cod_ibge=sistema_cultura
        .ente_federado.cod_ibge)
    assert sistema_atualizado.processo_sei == "123456"


def test_retorno_200_para_detalhar_ente(client, sistema_cultura, login_staff):
    """ Testa se página de detalhamento do ente retorna 200 """

    url = reverse("gestao:detalhar", kwargs={"cod_ibge": sistema_cultura.ente_federado.cod_ibge})
    request = client.get(url)
    assert request.status_code == 200


def test_retorno_do_form_da_diligencia(url, client, login_staff):
    """ Testa se form retornado no contexto tem as opções corretas"""

    SITUACOES = (
        (0, "Em preenchimento"),
        (1, "Avaliando anexo"),
        (2, "Concluída"),
        (3, "Arquivo aprovado com ressalvas"),
        (4, "Arquivo danificado"),
        (5, "Arquivo incompleto"),
        (6, "Arquivo incorreto"),
    )

    orgao_gestor = mommy.make("Componente", tipo=1, situacao=1)
    sistema_cultura = mommy.make(
        "SistemaCultura",
        ente_federado__cod_ibge=123456,
        _fill_optional='cadastrador',
        orgao_gestor=orgao_gestor,
    )

    arquivo = SimpleUploadedFile("lei.txt", b"file_content", content_type="text/plain")
    orgao_gestor.arquivo = arquivo
    orgao_gestor.save()

    request = client.get(
        url.format(id=sistema_cultura.id, componente="orgao_gestor")
    )

    classificacao = set(
        request.context["form"].fields["classificacao_arquivo"].choices
    )

    assert classificacao.symmetric_difference(SITUACOES) == set()


def usuario_id_retornado_pelo_context_diligencia(
    url, client, plano_trabalho, login_staff
):
    """ Testa se o id do usuário enviado pelo context está correto """

    request = client.get(
        url.format(id=plano_trabalho.id, componente="orgao_gestor")
    )

    assert request.context["usuario_id"] == plano_trabalho.usuario.id


def test_criacao_diligencia_exclusiva_para_gestor(client, url, plano_trabalho, login):
    """Testa se ao tentar acessar a url de criação da diligência o usuário
    que não é autorizado é redirecionado para a tela de login"""

    url_diligencia = url.format(
        id=plano_trabalho.id, componente="orgao_gestor"
    )

    request = client.get(url_diligencia)

    url_redirect = request.url.split("http://testserver/")
    url_login = "/admin/login/?next={}".format(url_diligencia)

    assert request.status_code == 302
    assert url_redirect[0] == url_login


def test_listar_documentos(client, plano_trabalho, login_staff):
    """ Testa funcionalidade de listagem de entes federados para alterar seus documentos
    na tela de gestão """

    templates = [
        "listar_legislacao",
        "listar_orgao_gestor",
        "listar_fundo_cultura",
        "listar_conselho",
        "listar_plano",
    ]

    for template in templates:

        url = reverse("gestao:listar_documentos", kwargs={"template": template})
        response = client.get(url)

        for sisstema in response.context_data["object_list"]:
            assert sistema.estado_processo == 6


def test_alterar_documentos_orgao_gestor(client, login_staff):
    """ Testa se funcionalidade de alterar documento para orgão gestor na
    tela de gestão salva no field arquivo """

    orgao_gestor = mommy.make("Componente", tipo=1)
    sistema_cultura = mommy.make("SistemaCultura", _fill_optional='ente_federado',
        orgao_gestor=orgao_gestor)

    arquivo = SimpleUploadedFile(
        "orgao.txt", b"file_content", content_type="text/plain"
    )

    url = reverse("gestao:alterar_componente", kwargs={"pk": sistema_cultura.orgao_gestor.id,
        "componente": "orgao_gestor"})

    client.post(url, data={"arquivo": arquivo, "data_publicacao": "28/06/2018"})

    name = Componente.objects.first().arquivo.name.split("orgao_gestor/")[1]
    situacao = Componente.objects.first().situacao

    assert name == arquivo.name
    assert situacao == 1


def test_inserir_documentos_orgao_gestor(client, sistema_cultura, login_staff):
    """ Testa se funcionalidade de inserir documento para orgão gestor na
    tela de gestão salva no field arquivo """

    arquivo = SimpleUploadedFile(
        "orgao.txt", b"file_content", content_type="text/plain"
    )

    url = reverse("gestao:inserir_componente", kwargs={"pk": sistema_cultura.id,
        "componente": "orgao_gestor"})

    client.post(url, data={"arquivo": arquivo, "data_publicacao": "28/06/2018"})

    name = Componente.objects.last().arquivo.name.split("orgao_gestor/")[1]
    situacao = Componente.objects.last().situacao

    assert name == arquivo.name
    assert situacao == 1


def test_alterar_documentos_legislacao(client, login_staff):
    """ Testa se funcionalidade de alterar documento para sistema de cultura na
    tela de gestão salva no field arquivo """

    legislacao = mommy.make("Componente", tipo=0)
    sistema_cultura = mommy.make("SistemaCultura", _fill_optional='ente_federado',
        legislacao=legislacao)

    arquivo = SimpleUploadedFile(
        "sistema_cultura.txt", b"file_content", content_type="text/plain"
    )

    url = reverse(
        "gestao:alterar_componente", kwargs={"pk": sistema_cultura.legislacao.id,
        "componente": "legislacao"}
    )

    client.post(url, data={"arquivo": arquivo, "data_publicacao": "28/06/2018"})

    name = Componente.objects.first().arquivo.name.split("legislacao/")[1]
    situacao = Componente.objects.first().situacao

    assert name == arquivo.name
    assert situacao == 1


def test_inserir_documentos_legislacao(client, sistema_cultura, login_staff):
    """ Testa se funcionalidade de inserir documento para sistema de cultura na
    tela de gestão salva no field arquivo """

    arquivo = SimpleUploadedFile(
        "sistema_cultura.txt", b"file_content", content_type="text/plain"
    )

    url = reverse("gestao:inserir_componente", kwargs={"pk": sistema_cultura.id,
        "componente": "legislacao"})

    client.post(url, data={"arquivo": arquivo, "data_publicacao": "28/06/2018"})

    name = Componente.objects.last().arquivo.name.split("legislacao/")[1]
    situacao = Componente.objects.last().situacao

    assert name == arquivo.name
    assert situacao == 1


def test_inserir_documentos_fundo_cultura(client, sistema_cultura, login_staff):
    """ Testa se funcionalidade de inserir documento para o fundo de cultura na
    tela de gestão salva no field arquivo """

    arquivo = SimpleUploadedFile(
        "fundo_cultura.txt", b"file_content", content_type="text/plain"
    )

    url = reverse(
        "gestao:inserir_componente", kwargs={"pk": sistema_cultura.id,
        "componente": "fundo_cultura"}
    )

    client.post(url, data={"arquivo": arquivo, "data_publicacao": "28/06/2018"})

    name = Componente.objects.last().arquivo.name.split("fundo_cultura/")[1]
    situacao = Componente.objects.last().situacao

    assert name == arquivo.name
    assert situacao == 1


def test_alterar_documentos_fundo_cultura(client, login_staff):
    """ Testa se funcionalidade de alterar documento para o fundo de cultura na
    tela de gestão salva no field arquivo """

    fundo = mommy.make("Componente", tipo=2)
    sistema_cultura = mommy.make("SistemaCultura", _fill_optional='ente_federado',
        fundo_cultura=fundo)

    arquivo = SimpleUploadedFile(
        "fundo_cultura.txt", b"file_content", content_type="text/plain"
    )

    url = reverse(
        "gestao:alterar_componente", kwargs={"pk": sistema_cultura.fundo_cultura.id, 
        "componente": "fundo_cultura"}
    )

    client.post(url, data={"arquivo": arquivo, "data_publicacao": "28/06/2018"})

    name = Componente.objects.first().arquivo.name.split("fundo_cultura/")[1]
    situacao = Componente.objects.first().situacao

    assert name == arquivo.name
    assert situacao == 1


def test_inserir_documentos_plano_cultura(client, sistema_cultura, login_staff):
    """ Testa se funcionalidade de inserir documento para plano de cultura na
    tela de gestão salva no field arquivo """

    arquivo = SimpleUploadedFile(
        "plano_cultura.txt", b"file_content", content_type="text/plain"
    )

    url = reverse(
        "gestao:inserir_componente", kwargs={"pk": sistema_cultura.id, "componente": "plano"}
    )

    client.post(url, data={"arquivo": arquivo, "data_publicacao": "28/06/2018"})

    name = Componente.objects.last().arquivo.name.split("plano/")[1]
    situacao = Componente.objects.last().situacao

    assert name == arquivo.name
    assert situacao == 1


def test_alterar_documentos_plano_cultura(client, sistema_cultura, login_staff):
    """ Testa se funcionalidade de alterar documento para plano de cultura na
    tela de gestão salva no field arquivo """

    plano = mommy.make("Componente", tipo=4)
    sistema_cultura = mommy.make("SistemaCultura", _fill_optional='ente_federado',
        plano=plano)

    arquivo = SimpleUploadedFile(
        "plano_cultura.txt", b"file_content", content_type="text/plain"
    )

    url = reverse(
        "gestao:alterar_componente", kwargs={"pk": sistema_cultura.plano.id, "componente": "plano"}
    )

    client.post(url, data={"arquivo": arquivo, "data_publicacao": "28/06/2018"})

    name = Componente.objects.first().arquivo.name.split("plano/")[1]
    situacao = Componente.objects.first().situacao

    assert name == arquivo.name
    assert situacao == 1


def test_alterar_documentos_conselho_cultural(client, login_staff):
    """ Testa se funcionalidade de alterar documento para conselho cultural na
    tela de gestão salva no field arquivo """

    conselho = mommy.make("Componente", tipo=3)
    sistema_cultura = mommy.make("SistemaCultura", _fill_optional='ente_federado',
        conselho=conselho)

    arquivo = SimpleUploadedFile(
        "conselho_cultural.txt", b"file_content", content_type="text/plain"
    )

    url = reverse(
        "gestao:alterar_componente", kwargs={"pk": sistema_cultura.conselho.id, "componente": "conselho"}
    )

    client.post(url, data={"arquivo": arquivo, "data_publicacao": "28/06/2018"})

    name = Componente.objects.first().arquivo.name.split("conselho/")[1]
    situacao = Componente.objects.first().situacao

    assert name == arquivo.name
    assert situacao == 1


def test_inserir_documentos_conselho_cultural(client, sistema_cultura, login_staff):
    """ Testa se funcionalidade de inserção documentos para conselho cultural na
    tela de gestão salva no field arquivo """

    arquivo = SimpleUploadedFile(
        "conselho_cultural.txt", b"file_content", content_type="text/plain"
    )

    url = reverse("gestao:inserir_componente", kwargs={"pk": sistema_cultura.id, 
        "componente": "conselho"})

    client.post(url, data={"arquivo": arquivo, "data_publicacao": "28/06/2018"})

    name = Componente.objects.last().arquivo.name.split("conselho/")[1]
    situacao = Componente.objects.last().situacao

    assert name == arquivo.name
    assert situacao == 1


def test_retorna_200_para_diligencia_geral(client, url, login_staff):
    """ Testa se retonar 200 ao dar um get na diligencia geral """
    diligencia = mommy.make("DiligenciaSimples")
    sistema_cultura = mommy.make(
        "SistemaCultura",
        ente_federado__cod_ibge=123456,
        _fill_optional=["cadastrador"],
        diligencia=diligencia,
    )

    url = reverse(
        "gestao:diligencia_geral_adicionar", kwargs={"pk": sistema_cultura.id}
    )
    request = client.get(url)

    assert request.status_code == 200


def test_salvar_informacoes_no_banco_diligencia_geral(url, client, login_staff):
    """Testa se as informacoes validadas pelo form estao sendo salvas no banco"""
    sistema_cultura = mommy.make(
        "SistemaCultura", ente_federado__cod_ibge=123456, _fill_optional=["cadastrador"]
    )

    url = reverse(
        "gestao:diligencia_geral_adicionar", kwargs={"pk": sistema_cultura.id}
    )

    response = client.post(url, data={"classificacao_arquivo": "2", "texto_diligencia": "bla"})

    diligencia = DiligenciaSimples.objects.first()
    sistema_cultura = SistemaCultura.sistema.get(
        ente_federado__cod_ibge=sistema_cultura.ente_federado.cod_ibge
    )

    assert DiligenciaSimples.objects.count() == 1
    assert DiligenciaSimples.objects.first() == sistema_cultura.diligencia


def test_redirecionamento_de_pagina_apos_POST_diligencia_geral(
    url, client, login_staff
):
    """ Testa se há o redirecionamento de página após o POST da diligência """
    sistema_cultura = mommy.make(
        "SistemaCultura", ente_federado__cod_ibge=123456, _fill_optional=["cadastrador"]
    )

    url = reverse(
        "gestao:diligencia_geral_adicionar", kwargs={"pk": sistema_cultura.id}
    )
    request = client.post(url, data={"classificacao_arquivo": "2", "texto_diligencia": "Ta errado cara"})
    url_redirect = request.url.split("http://testserver/")

    diligencia = DiligenciaSimples.objects.first()

    assert url_redirect[0] == reverse(
        "gestao:detalhar", kwargs={"cod_ibge": sistema_cultura.ente_federado.cod_ibge}
    )
    assert request.status_code == 302


def test_situacoes_componentes_diligencia(url, client, login_staff):
    """ Testa as informações referentes aos componentes do
    plano de trabalho na diligência geral """
    legislacao = mommy.make("Componente", tipo=0, situacao=1, _create_files=True)
    orgao = mommy.make("Componente", tipo=1, situacao=2, _create_files=True)
    fundo = mommy.make("Componente", tipo=2, situacao=3, _create_files=True)
    conselho = mommy.make("Componente", tipo=3, situacao=4, _create_files=True)
    plano = mommy.make("Componente", tipo=4, situacao=5, _create_files=True)

    sistema_cultura = mommy.make(
        "SistemaCultura",
        ente_federado__cod_ibge=123456,
        _fill_optional=["cadastrador"],
        legislacao=legislacao,
        orgao_gestor=orgao,
        fundo_cultura=fundo,
        conselho=conselho,
        plano=plano,
    )

    url = reverse(
        "gestao:diligencia_geral_adicionar", kwargs={"pk": sistema_cultura.id}
    )
    response = client.get(url)

    situacoes = response.context["situacoes"]

    assert situacoes["legislacao"] == sistema_cultura.legislacao.get_situacao_display()
    assert (
        situacoes["orgao_gestor"] == sistema_cultura.orgao_gestor.get_situacao_display()
    )
    assert (
        situacoes["fundo_cultura"]
        == sistema_cultura.fundo_cultura.get_situacao_display()
    )
    assert situacoes["conselho"] == sistema_cultura.conselho.get_situacao_display()
    assert situacoes["plano"] == sistema_cultura.plano.get_situacao_display()


def test_tipo_diligencia_componente(url, client, plano_trabalho, login_staff):
    """ Testa criação da diligência específica de um componente"""
    orgao_gestor = mommy.make("Componente", tipo=1, situacao=1)
    sistema_cultura = mommy.make(
        "SistemaCultura",
        ente_federado__cod_ibge=123456,
        _fill_optional='cadastrador',
        orgao_gestor=orgao_gestor,
    )

    arquivo = SimpleUploadedFile("lei.txt", b"file_content", content_type="text/plain")
    orgao_gestor.arquivo = arquivo
    orgao_gestor.save()

    request = client.post(
        url.format(id=sistema_cultura.id, componente="orgao_gestor"),
        data={"classificacao_arquivo": "4", "texto_diligencia": "Ta errado cara"},
    )

    sistema_cultura.orgao_gestor.refresh_from_db()

    assert DiligenciaSimples.objects.count() == 1
    assert DiligenciaSimples.objects.first() == sistema_cultura.orgao_gestor.diligencia


def test_envio_email_diligencia_geral(client, login_staff):
    """ Testa envio do email para diligência geral """
    sistema_cultura = mommy.make(
        "SistemaCultura", _fill_optional="cadastrador", ente_federado__cod_ibge=123456
    )

    sistema_cultura.cadastrador.user.email = "teste@teste.com"
    sistema_cultura.cadastrador.user.save()

    url = reverse("gestao:diligencia_geral_adicionar", kwargs={"pk": sistema_cultura.id})
    request = client.post(url, data={"classificacao_arquivo": "3", "texto_diligencia": "Ta errado cara"})

    assert len(mail.outbox) == 1


def test_diligencia_geral_sem_componentes(url, client, plano_trabalho, login_staff):
    """ Testa se ao fazer a diligência geral de um ente federado
    sem componentes retorne componente inexistente"""

    sistema_cultura = mommy.make(
        "SistemaCultura",
        legislacao=None,
        orgao_gestor=None,
        plano=None,
        conselho=None,
        fundo_cultura=None,
        ente_federado__cod_ibge=123456,
        _fill_optional=["cadastrador"],
    )

    url = reverse(
        "gestao:diligencia_geral_adicionar", kwargs={"pk": sistema_cultura.id}
    )

    request = client.get(url)

    for situacao in request.context["situacoes"].values():
        assert situacao == "Inexistente"


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

    q = json.dumps({"estado": mg.pk})
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
    assert request.json()["results"][0]["text"] == mg.sigla


def test_filtra_ufs_por_nome(client):
    """ Testa se UfChain retorna a UF correta ao passar o nome"""

    Uf.objects.all().delete()
    mg = mommy.make("Uf", sigla="MG", nome_uf="Minas Gerais")
    mommy.make("Uf", _quantity=10)

    url = "{url}?q={param}".format(url=reverse("gestao:uf_chain"), param="Minas")
    request = client.get(url)

    assert len(request.json()["results"]) == 1
    assert request.json()["results"][0]["text"] == mg.sigla


def test_acompanhar_adesao_ordenar_data_um_componente_por_sistema(client, login_staff):
    """ Testa ordenação da página de acompanhamento das adesões
    por data de envio mais antiga entre os componentes"""

    sistema_sem_analise_recente = mommy.make('SistemaCultura',
        estado_processo = '6',
        ente_federado__cod_ibge=123450,
        _fill_optional='legislacao')
    sistema_sem_analise_recente.legislacao.situacao = 1
    sistema_sem_analise_recente.legislacao.data_envio = datetime.date(2018, 1, 1)
    sistema_sem_analise_recente.legislacao.save()

    sistema_sem_analise_antigo = mommy.make('SistemaCultura',
        estado_processo = '6',
        ente_federado__cod_ibge=123457,
        _fill_optional='orgao_gestor')
    sistema_sem_analise_antigo.orgao_gestor.situacao = 1
    sistema_sem_analise_antigo.orgao_gestor.data_envio = datetime.date(2017, 1, 1)
    sistema_sem_analise_antigo.orgao_gestor.save()

    sistema_com_diligencia_antigo = mommy.make('SistemaCultura',
        estado_processo = '6',
        ente_federado__cod_ibge=123458,
        _fill_optional='fundo_cultura')
    sistema_com_diligencia_antigo.fundo_cultura.situacao = 4
    sistema_com_diligencia_antigo.fundo_cultura.data_envio = datetime.date(2016, 1, 1)
    sistema_com_diligencia_antigo.fundo_cultura.save()

    sistema_com_analise_antigo = mommy.make('SistemaCultura',
        estado_processo = '6',
        ente_federado__cod_ibge=123459,
        _fill_optional='fundo_cultura')
    sistema_com_analise_antigo.fundo_cultura.situacao = 2
    sistema_com_analise_antigo.fundo_cultura.data_envio = datetime.date(2016, 1, 1)
    sistema_com_analise_antigo.fundo_cultura.save()

    url = reverse("gestao:acompanhar_adesao")
    response = client.get(url)

    assert response.context_data['object_list'][0] == sistema_sem_analise_antigo
    assert response.context_data['object_list'][1] == sistema_sem_analise_recente
    assert response.context_data['object_list'][2] == sistema_com_diligencia_antigo
    assert response.context_data['object_list'][3] == sistema_com_analise_antigo


def test_acompanhar_adesao_mais_de_um_sistema_por_ente(client, login_staff):
    """ Testa ordenação da página de acompanhamento das adesões
    por data de envio mais antiga entre os componentes"""

    ente_federado_1 = mommy.make('EnteFederado', cod_ibge=123450)
    sistema_sem_analise_recente_1 = mommy.make('SistemaCultura',
        estado_processo = '6',
        ente_federado=ente_federado_1,
        _fill_optional='legislacao')
    sistema_sem_analise_recente_1.legislacao.situacao = 1
    sistema_sem_analise_recente_1.legislacao.data_envio = datetime.date(2017, 1, 1)
    sistema_sem_analise_recente_1.legislacao.save()

    sistema_sem_analise_recente_2 = mommy.make('SistemaCultura',
        estado_processo = '6',
        ente_federado=ente_federado_1,
        _fill_optional='legislacao')
    sistema_sem_analise_recente_2.legislacao.situacao = 1
    sistema_sem_analise_recente_2.legislacao.data_envio = datetime.date(2018, 1, 1)
    sistema_sem_analise_recente_2.legislacao.save()

    ente_federado_2 = mommy.make('EnteFederado', cod_ibge=123457)
    sistema_sem_analise_antigo_1 = mommy.make('SistemaCultura',
        estado_processo = '6',
        ente_federado=ente_federado_2,
        _fill_optional='orgao_gestor')
    sistema_sem_analise_antigo_1.orgao_gestor.situacao = 1
    sistema_sem_analise_antigo_1.orgao_gestor.data_envio = datetime.date(1990, 1, 1)
    sistema_sem_analise_antigo_1.orgao_gestor.save()

    sistema_sem_analise_antigo_2 = mommy.make('SistemaCultura',
        estado_processo = '6',
        ente_federado=ente_federado_2,
        _fill_optional='orgao_gestor')
    sistema_sem_analise_antigo_2.orgao_gestor.situacao = 1
    sistema_sem_analise_antigo_2.orgao_gestor.data_envio = datetime.date(1980, 1, 1)
    sistema_sem_analise_antigo_2.orgao_gestor.save()

    url = reverse("gestao:acompanhar_adesao")
    response = client.get(url)

    assert response.context_data['object_list'][0] == sistema_sem_analise_antigo_2
    assert response.context_data['object_list'][1] == sistema_sem_analise_recente_2

def test_acompanhar_adesao_ordenar_data_com_sistema_com_mais_de_um_componente(client, login_staff):
    """ Testa se na página de acompanhamento de adesões, quando há sistemas com múltiplos 
    componentes, o correto é considerado para ordenação pela data """

    sistema_1 = mommy.make('SistemaCultura',
        estado_processo = '6',
        ente_federado__cod_ibge=123456,
        _fill_optional=['legislacao', 'orgao_gestor'])

    sistema_1.legislacao.situacao = 5
    sistema_1.legislacao.data_envio = datetime.date(2016, 1, 1)
    sistema_1.legislacao.save()

    sistema_1.orgao_gestor.situacao = 1
    sistema_1.orgao_gestor.data_envio = datetime.date(2017, 1, 1)
    sistema_1.orgao_gestor.save()

    sistema_2 = mommy.make('SistemaCultura',
        estado_processo = '6',
        ente_federado__cod_ibge=123457,
        _fill_optional=['fundo_cultura', 'plano'])

    sistema_2.fundo_cultura.situacao = 4
    sistema_2.fundo_cultura.data_envio = datetime.date(2017, 1, 1)
    sistema_2.fundo_cultura.save()

    sistema_2.plano.situacao = 3
    sistema_2.plano.data_envio = datetime.date(2018, 1, 1)
    sistema_2.plano.save()

    sistema_3 = mommy.make('SistemaCultura',
        estado_processo = '6',
        ente_federado__cod_ibge=123458,
        _fill_optional='conselho')

    sistema_3.conselho.situacao = 1
    sistema_3.conselho.data_envio = datetime.date(2018, 1, 1)
    sistema_3.conselho.save()

    url = reverse("gestao:acompanhar_adesao")
    response = client.get(url)

    assert len(response.context_data['object_list']) == 3
    assert response.context_data['object_list'][0] == sistema_1
    assert response.context_data['object_list'][1] == sistema_3
    assert response.context_data['object_list'][2] == sistema_2


def test_acompanhar_adesao_ordenar_estado_processo(client, login_staff):
    """ Testa ordenação da página de acompanhamento das adesões
    por data de envio mais antiga entre os componentes e
    estado do processo da adesão """

    sistema_nao_publicado = mommy.make('SistemaCultura', estado_processo=1,
                    ente_federado__cod_ibge=123456,
                    _fill_optional=['legislacao', 'cadastrador'])

    sistema_publicado = mommy.make('SistemaCultura', estado_processo=6,
                    ente_federado__cod_ibge=123457,
                    _fill_optional=['legislacao', 'cadastrador'])
    sistema_publicado.legislacao.situacao = 1
    sistema_publicado.legislacao.save()

    sistema_sem_cadastrador = mommy.make('SistemaCultura', cadastrador=None,
                    ente_federado__cod_ibge=123458,
                    _fill_optional='legislacao')

    url = reverse("gestao:acompanhar_adesao")
    response = client.get(url)

    assert response.context_data['object_list'][0] == sistema_publicado
    assert response.context_data['object_list'][1] == sistema_nao_publicado
    assert response.context_data['object_list'][2] == sistema_sem_cadastrador


def test_alterar_dados_adesao_detalhe_municipio(client, login_staff, sistema_cultura):
    """ Testa alterar os dados da adesão na tela de detalhe do município """

    url = reverse("gestao:alterar_dados_adesao", kwargs={"cod_ibge": 
        sistema_cultura.ente_federado.cod_ibge})

    data = {
        "estado_processo": '6',
        "data_publicacao_acordo": datetime.date.today(),
        "processo_sei": "123456765",
        "justificativa": "texto de justificativa",
        "localizacao": "1234567890",
        "link_publicacao_acordo": "https://www.google.com",
    }

    response = client.post(url, data=data)

    sistema_atualizado = SistemaCultura.sistema.get(ente_federado__cod_ibge=sistema_cultura
        .ente_federado.cod_ibge)

    #assert response.status_code == 302
    assert sistema_atualizado.estado_processo == "6"
    assert sistema_atualizado.data_publicacao_acordo == datetime.date.today()
    assert sistema_atualizado.processo_sei == "123456765"
    assert sistema_atualizado.justificativa == "texto de justificativa"
    assert sistema_atualizado.localizacao == "1234567890"
    assert sistema_atualizado.link_publicacao_acordo == "https://www.google.com"


def test_alterar_dados_adesao_sem_valores(client, login_staff, sistema_cultura):
    """ Testa retorno ao tentar alterar os dados da adesão sem passar dados válidos """

    url = reverse("gestao:alterar_dados_adesao", kwargs={"cod_ibge": 
        sistema_cultura.ente_federado.cod_ibge})
    data = {}

    response = client.post(url, data=data)

    sistema_atualizado = SistemaCultura.sistema.get(ente_federado__cod_ibge=sistema_cultura
        .ente_federado.cod_ibge)

    #assert response.status_code == 302
    assert sistema_atualizado.estado_processo == "0"
    assert not sistema_atualizado.data_publicacao_acordo
    assert not sistema_atualizado.processo_sei
    assert not sistema_atualizado.justificativa
    assert not sistema_atualizado.localizacao
    assert not sistema_atualizado.link_publicacao_acordo


def test_alterar_cadastrador_sem_data_publicacao(client, login_staff):
    """ Testa alteração de cadastrador de um sistema cultura
    sem data de publicação do acordo """

    new_user = mommy.make('Usuario', user__username='34701068004')
    sistema = mommy.make('SistemaCultura', ente_federado__cod_ibge=123456)

    url = reverse('gestao:alterar_cadastrador', kwargs={'cod_ibge': sistema.ente_federado.cod_ibge})

    data = {
        'cpf_cadastrador': new_user.user.username,
    }

    client.post(url, data=data)

    sistema_atualizado = SistemaCultura.sistema.get(ente_federado__cod_ibge=sistema.ente_federado.cod_ibge)
    assert sistema_atualizado.cadastrador == new_user


def test_alterar_cadastrador_com_data_publicacao(client, login_staff):
    """ Testa alteração de cadastrador de um sistema cultura 
    com data de publicação do acordo"""

    new_user = mommy.make('Usuario', user__username='34701068004')
    sistema = mommy.make('SistemaCultura', ente_federado__cod_ibge=123456)

    url = reverse('gestao:alterar_cadastrador', kwargs={'cod_ibge': sistema.ente_federado.cod_ibge})

    data = {
        'cpf_cadastrador': new_user.user.username,
        'data_publicacao_acordo': "2016-02-02"
    }

    client.post(url, data=data)

    sistema_atualizado = SistemaCultura.sistema.get(ente_federado__cod_ibge=sistema.ente_federado.cod_ibge)
    assert sistema_atualizado.cadastrador == new_user
    assert sistema_atualizado.data_publicacao_acordo == datetime.date(2016, 2, 2)


def test_ajax_cadastrador_cpf(client, login_staff):
    """ Testa retorno de CPF do cadastrador de um ente federado municipal
    existente no sistema """

    url = reverse("gestao:ajax-consulta-cpf")

    client.login(username=login_staff.user.username, password="123456")

    response = client.post(
        url,
        data={"cpf": login_staff.user.username},
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )

    assert response.status_code == 200
    assert response.json()["data"]["nome"] == str(login_staff.nome_usuario)


def test_ajax_cadastrador_cpf_inexistente(client, login_staff):
    """ Testa retorno ao passar um cpf inexistente """

    url = reverse("gestao:ajax-consulta-cpf")

    client.login(username=login_staff.user.username, password="123456")

    response = client.post(
        url, data={"cpf": "123467890"}, HTTP_X_REQUESTED_WITH="XMLHttpRequest"
    )

    assert response.status_code == 404


def test_ajax_cadastrador_sem_cpf(client, login_staff):
    """ Testa retorno ao não passar um cpf """

    url = reverse("gestao:ajax-consulta-cpf")

    client.login(username=login_staff.user.username, password="123456")

    response = client.post(
        url, data={"cpf": ""}, HTTP_X_REQUESTED_WITH="XMLHttpRequest"
    )

    assert response.status_code == 400


def test_ajax_cadastrador_sem_requisicao_ajax(client, login_staff):
    """ Testa retorno ao não passar uma requisição ajax """

    url = reverse("gestao:ajax-consulta-cpf")

    client.login(username=login_staff.user.username, password="123456")

    response = client.post(url, data={"cpf": "123467890"})

    assert response.status_code == 400


def test_pesquisa_por_ente_federado_com_arquivo_lei_sistema(client, login_staff):
    """ Testa a pesquisa pelo nome (sem acento) de um Ente Federado
    que tenha o arquivo Lei Sistema aguardando análise
    """

    arquivo = SimpleUploadedFile(
        "orgao.txt", b"file_content", content_type="text/plain"
    )

    sistema = mommy.make(
        "SistemaCultura", ente_federado__cod_ibge=123456, ente_federado__nome="Abaeté", 
        estado_processo='6', _fill_optional='legislacao'
    )

    sistema.legislacao.situacao = 1
    sistema.legislacao.tipo = 0
    sistema.legislacao.data_envio = datetime.date(2018, 1, 1)
    sistema.legislacao.arquivo = arquivo
    sistema.legislacao.save()

    url = reverse("gestao:acompanhar_componente", kwargs={"componente":"legislacao"}) + "?q=Abaete&anexo=arquivo"
    response = client.get(url)

    assert response.context_data["object_list"][0] == sistema
    assert (
        response.context_data["object_list"][0].ente_federado.nome == "Abaeté"
    )


def test_pesquisa_por_ente_federado_com_arquivo_plano_cultura(client, login_staff):
    """ Testa a pesquisa pelo nome (sem acento) de um Ente Federado
    que tenha o arquivo Plano Cultura aguardando análise
    """

    arquivo = SimpleUploadedFile(
        "orgao.txt", b"file_content", content_type="text/plain"
    )

    sistema = mommy.make(
        "SistemaCultura", ente_federado__cod_ibge=123456, ente_federado__nome="Abaeté", 
        estado_processo='6', _fill_optional='plano'
    )

    sistema.plano.situacao = 1
    sistema.plano.tipo = 4
    sistema.plano.data_envio = datetime.date(2018, 1, 1)
    sistema.plano.arquivo = arquivo
    sistema.plano.save()

    url = reverse("gestao:acompanhar_componente", kwargs={"componente":"plano"}) + "?q=Abaete&anexo=arquivo"
    response = client.get(url)

    assert response.context_data["object_list"][0] == sistema
    assert (
        response.context_data["object_list"][0].ente_federado.nome == "Abaeté"
    )


def test_pesquisa_por_ente_federado_com_arquivo_fundo_cultura(client, login_staff):
    """ Testa a pesquisa pelo nome (sem acento) de um Ente Federado
    que tenha o arquivo Fundo Cultura aguardando análise
    """

    arquivo = SimpleUploadedFile(
        "orgao.txt", b"file_content", content_type="text/plain"
    )

    sistema = mommy.make(
        "SistemaCultura", ente_federado__cod_ibge=12346, ente_federado__nome="Abaeté", 
        estado_processo='6', _fill_optional='fundo_cultura'
    )

    sistema.fundo_cultura.situacao = 1
    sistema.fundo_cultura.tipo = 2
    sistema.fundo_cultura.data_envio = datetime.date(2018, 1, 1)
    sistema.fundo_cultura.arquivo = arquivo
    sistema.fundo_cultura.save()

    url = reverse("gestao:acompanhar_componente", kwargs={"componente":"fundo_cultura"}) + "?q=Abaete&anexo=arquivo"
    response = client.get(url)

    assert response.context_data["object_list"][0] == sistema
    assert (
        response.context_data["object_list"][0].ente_federado.nome == "Abaeté"
    )


def test_pesquisa_por_ente_federado_com_arquivo_orgao_gestor(client, login_staff):
    """ Testa a pesquisa pelo nome (sem acento) de um Ente Federado
    que tenha o arquivo Orgão Gestor aguardando análise
    """

    arquivo = SimpleUploadedFile(
        "orgao.txt", b"file_content", content_type="text/plain"
    )

    sistema = mommy.make(
        "SistemaCultura", ente_federado__cod_ibge=123456, ente_federado__nome="Abaeté", 
        estado_processo='6', _fill_optional='orgao_gestor'
    )

    sistema.orgao_gestor.situacao = 1
    sistema.orgao_gestor.tipo = 1
    sistema.orgao_gestor.data_envio = datetime.date(2018, 1, 1)
    sistema.orgao_gestor.arquivo = arquivo
    sistema.orgao_gestor.save()

    url = reverse("gestao:acompanhar_componente", kwargs={"componente":"orgao_gestor"}) + "?q=Abaete&anexo=arquivo"
    response = client.get(url)

    assert response.context_data["object_list"][0] == sistema
    assert (
        response.context_data["object_list"][0].ente_federado.nome == "Abaeté"
    )


def test_pesquisa_por_ente_federado_com_arquivo_conselho_cultural(client, login_staff):
    """ Testa a pesquisa pelo nome (sem acento) de um Ente Federado
    que tenha o arquivo Conselho Cultural aguardando análise
    """

    arquivo = SimpleUploadedFile(
        "orgao.txt", b"file_content", content_type="text/plain"
    )

    sistema = mommy.make(
        "SistemaCultura", ente_federado__cod_ibge=123456, ente_federado__nome="Abaeté", 
        estado_processo='6', _fill_optional='conselho'
    )

    sistema.conselho.situacao = 1
    sistema.conselho.tipo = 3
    sistema.conselho.data_envio = datetime.date(2018, 1, 1)
    sistema.conselho.arquivo = arquivo
    sistema.conselho.save()

    url = reverse("gestao:acompanhar_componente", kwargs={"componente":"conselho"}) + "?q=Abaete&anexo=arquivo"
    response = client.get(url)

    assert response.context_data["object_list"][0] == sistema
    assert (
        response.context_data["object_list"][0].ente_federado.nome == "Abaeté"
    )


def test_pesquisa_por_ente_federado_inserir_documentos_listar_sistemas(
    client, login_staff
):
    """ Testa a pesquisa pelo nome (sem acento) de um Ente Federado na tela
    de listar documentos de sistemas de Cultura
    """

    ente = mommy.make("EnteFederado", nome="Abaeté", cod_ibge=123456)
    sistema_cultura = mommy.make("SistemaCultura", estado_processo=6, 
        ente_federado=ente)

    url = (
        reverse("gestao:listar_documentos", kwargs={"template": "listar_legislacao"})
        + "?q=Abaete"
    )
    response = client.get(url)

    assert response.context_data["object_list"][0].ente_federado == sistema_cultura.ente_federado


def test_pesquisa_por_ente_federado_inserir_documentos_listar_orgaos(
    client, login_staff
):
    """ Testa a pesquisa pelo nome (sem acento) de um Ente Federado na tela
    de listar documentos de Ogãos
    """

    ente = mommy.make("EnteFederado", nome="Abaeté", cod_ibge=123456)
    sistema_cultura = mommy.make("SistemaCultura", estado_processo=6, 
        ente_federado=ente)

    url = (
        reverse("gestao:listar_documentos", kwargs={"template": "listar_orgao_gestor"})
        + "?q=Abaete"
    )
    response = client.get(url)

    assert response.context_data["object_list"][0].ente_federado == sistema_cultura.ente_federado


def test_pesquisa_por_ente_federado_inserir_documentos_listar_conselhos(
    client, login_staff
):
    """ Testa a pesquisa pelo nome (sem acento) de um Ente Federado na tela de listar documentos de Conselhos
    """

    ente = mommy.make("EnteFederado", nome="Abaeté", cod_ibge=123456)
    sistema_cultura = mommy.make("SistemaCultura", estado_processo=6, 
        ente_federado=ente)

    url = (
        reverse("gestao:listar_documentos", kwargs={"template": "listar_conselho"})
        + "?q=Abaete"
    )
    response = client.get(url)

    assert response.context_data["object_list"][0].ente_federado == sistema_cultura.ente_federado


def test_pesquisa_por_ente_federado_inserir_documentos_listar_fundos(
    client, login_staff
):
    """ Testa a pesquisa pelo nome (sem acento) de um Ente Federado na tela de listar documentos de fundos
    """

    ente = mommy.make("EnteFederado", nome="Abaeté", cod_ibge=123456)
    sistema_cultura = mommy.make("SistemaCultura", estado_processo=6, 
        ente_federado=ente)

    url = (
        reverse("gestao:listar_documentos", kwargs={"template": "listar_fundo_cultura"})
        + "?q=Abaete"
    )
    response = client.get(url)

    assert response.context_data["object_list"][0].ente_federado == sistema_cultura.ente_federado


def test_pesquisa_por_ente_federado_inserir_documentos_listar_planos(
    client, login_staff):
    """ Testa a pesquisa pelo nome (sem acento) de um Ente Federado na tela de listar documentos de planos de Cultura
    """

    ente = mommy.make("EnteFederado", nome="Abaeté", cod_ibge=123456)
    sistema_cultura = mommy.make("SistemaCultura", estado_processo=6, 
        ente_federado=ente)

    url = (
        reverse("gestao:listar_documentos", kwargs={"template": "listar_plano"})
        + "?q=Abaete"
    )
    response = client.get(url)

    assert response.context_data["object_list"][0].ente_federado == sistema_cultura.ente_federado


def test_adicionar_prazo_permanecendo_na_mesma_pagina_apos_redirect(
    client, login_staff
):
    """ Testa se ao adicionar prazo a um Ente Federado, a tela permanecerá na mesma página (verificação pela url) """

    users = mommy.make(
        "Usuario", _fill_optional=["plano_trabalho", "municipio"], _quantity=15
    )

    for user in users:
        user.estado_processo = "6"
        user.data_publicacao_acordo = datetime.date(2018, 1, 1)
        user.save()

    page = 2

    url = reverse(
        "gestao:aditivar_prazo", kwargs={"id": str(users[14].id), "page": str(page)}
    )
    request = client.post(url)

    assert request.url == "/gestao/acompanhar/prazo/?page={}".format(page)
    assert request.status_code == 302


def test_se_o_ente_permanece_na_mesma_pagina_apos_adicionar_prazo(client, login_staff):
    """ Testa se ao adicionar prazo a um Ente Federado, o Ente permanecerá na mesma página após
    sucesso ao adicionar prazo (verificação pelo id do usuário na lista de entes)"""

    resposta_ok = False
    uf = mommy.make("Uf", nome_uf="Acre", sigla="AC")

    users = mommy.make(
        "Usuario",
        prazo=2,
        estado_processo=6,
        data_publicacao_acordo=datetime.date(2018, 1, 1),
        _fill_optional=["plano_trabalho"],
        _quantity=20,
    )

    users[0].municipio = mommy.make(
        "Municipio",
        cidade=mommy.make("Cidade", nome_municipio="AAAAAA", uf=uf),
        estado=uf,
        cnpj_prefeitura="13.348.479/0001-01",
    )
    users[0].save()

    for user in users[1:19]:
        user.municipio = mommy.make(
            "Municipio",
            estado=uf,
            cidade=mommy.make("Cidade", uf=uf),
            cnpj_prefeitura="13.348.479/0001-01",
        )
        user.save()

    url = reverse("gestao:aditivar_prazo", kwargs={"id": str(users[0].id), "page": "1"})
    request = client.post(url)
    url_apos_redirect = request.url

    response = client.get(url_apos_redirect)

    if users[0] in response.context_data["object_list"]:
        resposta_ok = True

    assert resposta_ok == True
    assert request.status_code == 302
    assert response.context_data["object_list"][0] == users[0]


def test_pesquisa_de_ente_federado_sem_acento_tela_adicionar_prazo(client, login_staff):
    """ Testa a pesquisa por nome do ente federado (sem acento) - Deve retornar o nome
    com o acento normalmente """

    municipio = mommy.make(
        "Municipio", cidade=mommy.make("Cidade", nome_municipio="Acrelândia")
    )

    user = mommy.make("Usuario", _fill_optional=["plano_trabalho"], municipio=municipio)
    user.estado_processo = "6"
    user.save()
    user.data_publicacao_acordo = datetime.date(2018, 1, 1)
    user.save()

    url = reverse("gestao:acompanhar_prazo") + "?municipio=Acrelandia"
    response = client.get(url)

    assert response.context_data["object_list"][0].municipio == user.municipio
    assert (
        response.context_data["object_list"][0].municipio.cidade.nome_municipio
        == "Acrelândia"
    )
