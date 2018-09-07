import pytest

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core import mail
from django.conf import settings
from django.shortcuts import reverse

from model_mommy import mommy

from adesao.models import Municipio

pytestmark = pytest.mark.django_db


def test_index_page(client):
    url = reverse("adesao:index")
    response = client.get(url)

    assert response.status_code == 200


def test_incorrect_login_index_page(client):
    """ Caso o login falhe redireciona para tela inicial com os erros """

    url = reverse("adesao:login")
    response = client.post(url, data={"username": "", "password": ""})

    assert response.status_code == 200
    assert response.context_data["form"].errors


def test_home_page(client, login):
    url = reverse("adesao:home")
    response = client.get(url)

    assert response.status_code == 200


def test_envio_email_em_nova_adesao(client):
    user = User.objects.create(username="teste")
    user.set_password("123456")
    user.save()
    usuario = mommy.make("Usuario", user=user)

    estado = mommy.make("Uf")
    cidade = mommy.make("Cidade")

    client.login(username=user.username, password="123456")

    response = client.post(
        "/adesao/municipio/cadastrar/0/",
        {
            "estado": estado.codigo_ibge,
            "cidade": cidade.id,
            "cnpj_prefeitura": "95.876.554/0001-63",
            "cpf_prefeito": "381.390.630-29",
            "uf": estado,
            "rg_prefeito": "48.464.068-9",
            "orgao_expeditor_rg": "SSP",
            "estado_expeditor": estado.codigo_ibge,
            "nome_prefeito": "Joao silva",
            "email_institucional_prefeito": "joao@email.com",
            "endereco_eletronico": "teste.com.br",
            "cep": "60751-110",
            "complemento": "casa 22",
            "bairro": "rua teste",
            "telefone_um": "6299999999",
            "endereco": "rua do pao",
            "termo_posse_prefeito": SimpleUploadedFile(
                "test_file.pdf", bytes("test text", "utf-8")
            ),
            "cpf_copia_prefeito": SimpleUploadedFile(
                "test_file2.pdf", bytes("test text", "utf-8")
            ),
            "rg_copia_prefeito": SimpleUploadedFile(
                "test_file2.pdf", bytes("test text", "utf-8")
            ),
        },
    )

    # Acessa a url de sucesso após o cadastro para fazer o envio do email
    client.get(response.url)

    municipio = Municipio.objects.last()

    texto = f"""Prezado Gestor,

Um novo ente federado acabou de se cadastrar e fazer a solicitação de nova adesão.
Segue abaixo os dados de contato do ente federado:

Dados do Ente Federado:
Cadastrador: {usuario.nome_usuario}
Nome do Prefeito: {municipio.nome_prefeito}
Cidade: {cidade.nome_municipio}
Estado: {estado.sigla}
Email Institucional: {municipio.email_institucional_prefeito}
Telefone de Contato: {municipio.telefone_um}
Link da Adesão: http://snc.cultura.gov.br/gestao/detalhar/municipio/{usuario.id}

Equipe SNC
Ministério da Cultura"""

    assert len(mail.outbox) == 1
    assert (
        mail.outbox[0].subject
        == "MINISTÉRIO DA CULTURA - SNC - SOLICITAÇÃO NOVA ADESÃO"
    )
    assert mail.outbox[0].from_email == "naoresponda@cultura.gov.br"
    assert mail.outbox[0].to == [settings.RECEIVER_EMAIL]
    assert mail.outbox[0].body == texto


def test_envio_email_em_esqueceu_senha(client):
    mommy.make("Site", name="SNC", domain="snc.cultura.gov.br")

    user = User.objects.create(username="teste", email="test@email.com")
    user.set_password("123456")
    user.save()
    usuario = mommy.make("Usuario", user=user)

    client.post("/password_reset/", {"email": usuario.user.email})

    assert len(mail.outbox) == 1


def test_template_em_esqueceu_senha(client):

    response = client.get("/password_reset/")

    assert response.template_name[0] == "registration/password_reset_form.html"

    # Pelo fato de o template padrão do django ter esse mesmo nome fizemos uma validação a mais
    assert "Sistema Nacional de Cultura" in response.rendered_content


def test_cadastro_de_um_ente_tipo_estado(login, client):
    """Testa a situação da Issue #251 Erro ao Cadastrar um ente do tipo Estado
    Ao cadastrar um ente do tipo estado, um erro ocorre ao enviar o
    email de confirmação ao cadastrador. A falta da Cidade nas
    informações faz com que o sistema dispare uma exceção e interrompa
    a execução.
    """

    url = reverse("adesao:cadastrar_municipio", kwargs={"tipo_ente": 1})
    estado = mommy.make("Uf")

    client.force_login(login.user)

    response = client.post(
        url,
        {
            "estado": estado.codigo_ibge,
            "cnpj_prefeitura": "95.876.554/0001-63",
            "cpf_prefeito": "381.390.630-29",
            "uf": estado,
            "rg_prefeito": "48.464.068-9",
            "orgao_expeditor_rg": "SSP",
            "estado_expeditor": estado.codigo_ibge,
            "nome_prefeito": "Joao silva",
            "email_institucional_prefeito": "joao@email.com",
            "endereco_eletronico": "teste.com.br",
            "cep": "60751-110",
            "complemento": "casa 22",
            "bairro": "rua teste",
            "telefone_um": "6299999999",
            "endereco": "rua do pao",
            "termo_posse_prefeito": SimpleUploadedFile(
                "test_file.pdf", bytes("test text", "utf-8")
            ),
            "cpf_copia_prefeito": SimpleUploadedFile(
                "test_file2.pdf", bytes("test text", "utf-8")
            ),
            "rg_copia_prefeito": SimpleUploadedFile(
                "test_file2.pdf", bytes("test text", "utf-8")
            ),
        },
    )

    client.get(response.url)
    assert len(mail.outbox) == 1
