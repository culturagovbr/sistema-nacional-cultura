import pytest

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core import mail
from django.conf import settings
from django.shortcuts import reverse
from django.forms.models import model_to_dict

from model_mommy import mommy

from adesao.models import Municipio, Funcionario, EnteFederado, Gestor, Sede, SistemaCultura

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


def test_consultar_informações_municipios(client):

    municipio = mommy.make(
        "SistemaCultura", ente_federado__cod_ibge=123456, ente_federado__nome="Brasília", 
        estado_processo='6'
    )

    url = reverse("adesao:consultar", kwargs={"tipo":"municipio"}) + "?ente_federado=Brasília"
    response = client.get(url)

    assert len(response.context_data["object_list"]) == 1
    assert response.context_data["object_list"][0] == municipio


def test_consultar_informações_estados(client):

    estado = mommy.make(
        "SistemaCultura", ente_federado__cod_ibge=12, ente_federado__nome="Acre", 
        estado_processo='6'
    )

    url = reverse("adesao:consultar", kwargs={"tipo":"estado"}) + "?ente_federado=Acre"
    response = client.get(url)

    assert len(response.context_data["object_list"]) == 1
    assert response.context_data["object_list"][0] == estado


def test_cadastrar_funcionario_tipo_responsavel(login, client):

    sistema_cultura = mommy.make("SistemaCultura", _fill_optional=['ente_federado',
        'sede', 'gestor'], cadastrador=login)

    funcionario = Funcionario(cpf="381.390.630-29", rg="48.464.068-9",
        orgao_expeditor_rg="SSP", estado_expeditor=29,
        nome="Joao silva", email_institucional="joao@email.com")

    url = reverse("adesao:home")
    client.get(url)

    url = reverse("adesao:cadastrar_funcionario",
        kwargs={"tipo": "responsavel", "sistema": sistema_cultura.id})

    response = client.post(
        url,
        {
            "cpf": funcionario.cpf,
            "rg": funcionario.rg,
            "orgao_expeditor_rg": funcionario.orgao_expeditor_rg,
            "estado_expeditor": 29,
            "nome": funcionario.nome,
            "email_institucional": funcionario.email_institucional,
            "telefone_um": "999999999"
        },
    )

    funcionario_salvo = Funcionario.objects.last()
    sistema_cultura_atualizado = SistemaCultura.sistema.get(
        ente_federado=sistema_cultura.ente_federado)

    assert sistema_cultura_atualizado.responsavel == funcionario_salvo
    assert funcionario_salvo.cpf == funcionario.cpf
    assert funcionario_salvo.rg == funcionario.rg
    assert funcionario_salvo.orgao_expeditor_rg == funcionario.orgao_expeditor_rg
    assert funcionario_salvo.estado_expeditor == funcionario.estado_expeditor
    assert funcionario_salvo.nome == funcionario.nome
    assert funcionario_salvo.email_institucional == funcionario.email_institucional
    assert funcionario_salvo.tipo_funcionario == 1
    assert client.session['sistema_cultura_selecionado'] == model_to_dict(sistema_cultura_atualizado, 
        exclude=['data_criacao', 'alterado_em'])


def test_cadastrar_funcionario_tipo_secretario(login, client):

    sistema_cultura = mommy.make("SistemaCultura", _fill_optional=['ente_federado',
        'gestor', 'sede'], cadastrador=login)

    funcionario = Funcionario(cpf="381.390.630-29", rg="48.464.068-9",
        orgao_expeditor_rg="SSP", estado_expeditor=29,
        nome="Joao silva", email_institucional="joao@email.com")

    url = reverse("adesao:home")
    client.get(url)

    url = reverse("adesao:cadastrar_funcionario",
        kwargs={"tipo": "secretario", "sistema": sistema_cultura.id})

    response = client.post(
        url,
        {
            "cpf": funcionario.cpf,
            "rg": funcionario.rg,
            "orgao_expeditor_rg": funcionario.orgao_expeditor_rg,
            "estado_expeditor": 29,
            "nome": funcionario.nome,
            "email_institucional": funcionario.email_institucional,
            "telefone_um": "999999999"
        },
    )

    funcionario_salvo = Funcionario.objects.last()
    sistema_cultura_atualizado = SistemaCultura.sistema.get(
        ente_federado=sistema_cultura.ente_federado)

    assert sistema_cultura_atualizado.secretario == funcionario_salvo
    assert funcionario_salvo.cpf == funcionario.cpf
    assert funcionario_salvo.rg == funcionario.rg
    assert funcionario_salvo.orgao_expeditor_rg == funcionario.orgao_expeditor_rg
    assert funcionario_salvo.estado_expeditor == funcionario.estado_expeditor
    assert funcionario_salvo.nome == funcionario.nome
    assert funcionario_salvo.email_institucional == funcionario.email_institucional
    assert funcionario_salvo.tipo_funcionario == 0
    assert client.session['sistema_cultura_selecionado'] == model_to_dict(sistema_cultura_atualizado, 
        exclude=['data_criacao', 'alterado_em'])


def test_alterar_funcionario_tipo_secretario(login, client):

    secretario = mommy.make("Funcionario", tipo_funcionario=0)
    sistema_cultura = mommy.make("SistemaCultura", secretario=secretario)

    url = reverse("adesao:alterar_funcionario",
        kwargs={"tipo": "secretario", "pk": sistema_cultura.secretario.id})

    funcionario = Funcionario(cpf="381.390.630-29", rg="48.464.068-9",
        orgao_expeditor_rg="SSP", estado_expeditor=29,
        nome="Joao silva", email_institucional="joao@email.com")

    response = client.post(
        url,
        {
            "cpf": funcionario.cpf,
            "rg": funcionario.rg,
            "orgao_expeditor_rg": funcionario.orgao_expeditor_rg,
            "estado_expeditor": 29,
            "nome": funcionario.nome,
            "email_institucional": funcionario.email_institucional,
            "telefone_um": "999999999"
        },
    )

    sistema_cultura_atualizado = SistemaCultura.sistema.get(
        ente_federado=sistema_cultura.ente_federado)

    assert sistema_cultura_atualizado.secretario.cpf == funcionario.cpf
    assert sistema_cultura_atualizado.secretario.rg == funcionario.rg
    assert sistema_cultura_atualizado.secretario.orgao_expeditor_rg == funcionario.orgao_expeditor_rg
    assert sistema_cultura_atualizado.secretario.estado_expeditor == funcionario.estado_expeditor
    assert sistema_cultura_atualizado.secretario.nome == funcionario.nome
    assert sistema_cultura_atualizado.secretario.email_institucional == funcionario.email_institucional
    assert sistema_cultura_atualizado.secretario.tipo_funcionario == 0


def test_alterar_funcionario_tipo_responsavel(login, client):

    responsavel = mommy.make("Funcionario",tipo_funcionario=1)
    sistema_cultura = mommy.make("SistemaCultura", responsavel=responsavel)

    url = reverse("adesao:alterar_funcionario",
        kwargs={"tipo": "responsavel", "pk": sistema_cultura.responsavel.id})

    funcionario = Funcionario(cpf="381.390.630-29", rg="48.464.068-9",
        orgao_expeditor_rg="SSP", estado_expeditor=29,
        nome="Joao silva", email_institucional="joao@email.com")

    response = client.post(
        url,
        {
            "cpf": funcionario.cpf,
            "rg": funcionario.rg,
            "orgao_expeditor_rg": funcionario.orgao_expeditor_rg,
            "estado_expeditor": 29,
            "nome": funcionario.nome,
            "email_institucional": funcionario.email_institucional,
            "telefone_um": "999999999"
        },
    )

    sistema_cultura_atualizado = SistemaCultura.sistema.get(
        ente_federado=sistema_cultura.ente_federado)

    assert sistema_cultura_atualizado.responsavel.cpf == funcionario.cpf
    assert sistema_cultura_atualizado.responsavel.rg == funcionario.rg
    assert sistema_cultura_atualizado.responsavel.orgao_expeditor_rg == funcionario.orgao_expeditor_rg
    assert sistema_cultura_atualizado.responsavel.estado_expeditor == funcionario.estado_expeditor
    assert sistema_cultura_atualizado.responsavel.nome == funcionario.nome
    assert sistema_cultura_atualizado.responsavel.email_institucional == funcionario.email_institucional
    assert sistema_cultura_atualizado.responsavel.tipo_funcionario == 1


def test_cadastrar_funcionario_dados_invalidos(login, client, sistema_cultura):

    url = reverse("adesao:cadastrar_funcionario",
        kwargs={"tipo": "secretario", "sistema": sistema_cultura.id})

    funcionario = Funcionario(cpf="123456", rg="48.464.068-9",
        orgao_expeditor_rg="SSP", estado_expeditor=29,
        nome="Joao silva", email_institucional="joao@email.com")

    response = client.post(
        url,
        {
            "cpf": funcionario.cpf,
            "rg": funcionario.rg,
            "orgao_expeditor_rg": funcionario.orgao_expeditor_rg,
            "estado_expeditor": 29,
            "nome": funcionario.nome,
            "email_institucional": funcionario.email_institucional,
            "telefone_um": "999999999"
        },
    )

    assert response.status_code == 200
    

def test_cadastrar_sistema_cultura_dados_validos(login, client, sistema_cultura):
    ente_federado = mommy.make("EnteFederado", cod_ibge=20563)
    gestor = Gestor(cpf="590.328.900-26", rg="1234567", orgao_expeditor_rg="ssp", estado_expeditor=29,
        nome="nome", telefone_um="123456", email_institucional="email@email.com", tipo_funcionario=2)
    sede = Sede(cnpj="70.658.964/0001-07", endereco="endereco", complemento="complemento",
        cep="72430101", bairro="bairro", telefone_um="123456")

    url = reverse("adesao:home")
    client.get(url)

    url = reverse("adesao:cadastrar_sistema")

    response = client.post(
        url,
        {
            "ente_federado": ente_federado.pk,
            "cpf": gestor.cpf,
            "rg": gestor.rg,
            "nome": gestor.nome,
            "orgao_expeditor_rg": gestor.orgao_expeditor_rg,
            "estado_expeditor": gestor.estado_expeditor,
            "telefone_um": gestor.telefone_um,
            "email_institucional": gestor.email_institucional,
            "tipo_funcionario": gestor.tipo_funcionario,
            "termo_posse": SimpleUploadedFile(
                "test_file.pdf", bytes("test text", "utf-8")
            ),
            "cpf_copia": SimpleUploadedFile(
                "test_file2.pdf", bytes("test text", "utf-8")
            ),
            "rg_copia": SimpleUploadedFile(
                "test_file2.pdf", bytes("test text", "utf-8")
            ),
            "cnpj": sede.cnpj,
            "endereco": sede.endereco,
            "complemento": sede.complemento,
            "cep": sede.cep,
            "bairro": sede.bairro,
            "telefone_um": sede.telefone_um,
        },
    )

    gestor_salvo = Gestor.objects.last()
    sede_salva = Sede.objects.last()
    sistema_salvo = SistemaCultura.sistema.get(ente_federado__nome=ente_federado.nome)

    assert sistema_salvo.ente_federado.cod_ibge == ente_federado.cod_ibge
    assert sistema_salvo.gestor == gestor_salvo
    assert sistema_salvo.sede == sede_salva
    assert sistema_salvo.cadastrador == login
    assert client.session['sistemas'][-1] == {"id": sistema_salvo.id, 
        "ente_federado__nome": sistema_salvo.ente_federado.nome}


def test_cadastrar_sistema_cultura_com_cadastrador_ja_possui_sistema(login, client):
    ente_federado = mommy.make("EnteFederado", cod_ibge=20563)
    gestor = Gestor(cpf="590.328.900-26", rg="1234567", orgao_expeditor_rg="ssp", estado_expeditor=29,
        nome="nome", telefone_um="123456", email_institucional="email@email.com", tipo_funcionario=2)
    sede = Sede(cnpj="70.658.964/0001-07", endereco="endereco", complemento="complemento",
        cep="72430101", bairro="bairro", telefone_um="123456")

    sistema_cultura = mommy.make("SistemaCultura", _fill_optional=['ente_federado', 
        'sede', 'gestor'], cadastrador=login)

    url = reverse("adesao:home")
    client.get(url)

    url = reverse("adesao:cadastrar_sistema")

    response = client.post(
        url,
        {
            "ente_federado": ente_federado.pk,
            "cpf": gestor.cpf,
            "rg": gestor.rg,
            "nome": gestor.nome,
            "orgao_expeditor_rg": gestor.orgao_expeditor_rg,
            "estado_expeditor": gestor.estado_expeditor,
            "telefone_um": gestor.telefone_um,
            "email_institucional": gestor.email_institucional,
            "tipo_funcionario": gestor.tipo_funcionario,
            "cnpj": sede.cnpj,
            "endereco": sede.endereco,
            "complemento": sede.complemento,
            "cep": sede.cep,
            "bairro": sede.bairro,
            "telefone_um": sede.telefone_um,
            "termo_posse": SimpleUploadedFile(
                "test_file.pdf", bytes("test text", "utf-8")
            ),
            "cpf_copia": SimpleUploadedFile(
                "test_file2.pdf", bytes("test text", "utf-8")
            ),
            "rg_copia": SimpleUploadedFile(
                "test_file2.pdf", bytes("test text", "utf-8")
            ),
        },
    )

    gestor_salvo = Gestor.objects.last()
    sede_salva = Sede.objects.last()
    sistema_salvo = SistemaCultura.objects.get(ente_federado=ente_federado)

    assert sistema_salvo.ente_federado.cod_ibge == ente_federado.cod_ibge
    assert sistema_salvo.gestor == gestor_salvo
    assert sistema_salvo.sede == sede_salva
    assert sistema_salvo.cadastrador == login
    assert login.sistema_cultura.count() == 2
    assert client.session['sistemas'][-1] == {"id": sistema_salvo.id, 
        "ente_federado__nome": sistema_salvo.ente_federado.nome}


def test_session_user_sem_sistema_cultura(login, client):

    url = reverse("adesao:home")
    response = client.get(url)

    assert 'sistema_cultura_selecionado' not in client.session


def test_session_user_com_um_sistema_cultura(login, client):

    sistema = mommy.make("SistemaCultura", _fill_optional=['ente_federado', 'secretario', 'responsavel',
        'gestor', 'sede'], gestor__tipo_funcionario=0, cadastrador=login)

    url = reverse("adesao:home")
    response = client.get(url)

    assert client.session['sistema_cultura_selecionado'] == model_to_dict(sistema, 
        exclude=['data_criacao', 'alterado_em'])
    assert client.session['sistema_situacao'] == sistema.get_estado_processo_display()
    assert client.session['sistema_sede'] == model_to_dict(sistema.sede)
    assert client.session['sistema_gestor'] == model_to_dict(sistema.gestor, exclude=['termo_posse', 'rg_copia', 'cpf_copia'])
    assert client.session['sistema_ente'] == model_to_dict(sistema.ente_federado, fields=['nome', 'cod_ibge'])


def test_session_user_com_mais_de_um_sistema_cultura(login, client):

    sistema_1 = mommy.make("SistemaCultura", _fill_optional=['ente_federado', 'secretario', 'responsavel'],
        cadastrador=login)
    sistema_2 = mommy.make("SistemaCultura", _fill_optional=['ente_federado', 'secretario', 'responsavel'],
        cadastrador=login)

    url = reverse("adesao:home")
    response = client.get(url)

    assert 'sistema_cultura_selecionado' not in client.session
    assert client.session['sistemas'][0]['id'] == sistema_1.id
    assert client.session['sistemas'][0]['ente_federado__nome'] == sistema_1.ente_federado.nome
    assert client.session['sistemas'][1]['id'] == sistema_2.id
    assert client.session['sistemas'][1]['ente_federado__nome'] == sistema_2.ente_federado.nome
    assert len(client.session['sistemas']) == 2


def test_importar_secretario(client, login):
    sistema_cultura = mommy.make("SistemaCultura", _fill_optional=['ente_federado', 'sede', 'gestor', 'secretario'],
        cadastrador=login)

    url = reverse("adesao:home")
    client.get(url)

    url = reverse("adesao:importar_secretario")
    response = client.get(url)

    sistema_atualizado = SistemaCultura.sistema.get(ente_federado=sistema_cultura.ente_federado)

    assert sistema_atualizado.responsavel == sistema_atualizado.secretario


def test_importar_secretario_id_invalido(client, login):
    sistema_cultura = mommy.make("SistemaCultura", _fill_optional=['ente_federado', 'sede', 'gestor'],
        cadastrador=login)

    url = reverse("adesao:home")
    client.get(url)

    url = reverse("adesao:importar_secretario")
    response = client.get(url)

    assert response.url == reverse("adesao:cadastrar_funcionario", kwargs={"sistema": sistema_cultura.id,
        "tipo": "responsavel"})


def test_detalhar_conselheiros(client):
    sistema_cultura = mommy.make("SistemaCultura", _fill_optional=['conselho'])
    conselheiro = mommy.make("Conselheiro", conselho=sistema_cultura.conselho)

    url = reverse("adesao:detalhar", kwargs={'pk': sistema_cultura.id})
    response = client.get(url)

    assert response.context_data['conselheiros'][0] == conselheiro