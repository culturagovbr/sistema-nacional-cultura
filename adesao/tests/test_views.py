import pytest

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core import mail
from django.conf import settings
from django.shortcuts import reverse
from django.forms.models import model_to_dict

from model_mommy import mommy

from adesao.models import Municipio, Funcionario, EnteFederado, Gestor, Sede, SistemaCultura
from adesao.models import Usuario

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


def test_envio_email_novo_usuario(client):

    url = reverse("adesao:usuario")

    response = client.post(
        url,
        {
            "username": "054.470.811-30",
            "email": "email@email.com",
            "confirmar_email": "email@email.com",
            "email_pessoal": "email@pessoal.com",
            "confirmar_email_pessoal": "email@pessoal.com",
            "nome_usuario": "Nome Teste",
            "password1": "123456",
            "password2": "123456",
        },
    )

    usuario = Usuario.objects.get(user__username='05447081130')

    texto = f"""Prezad@ Nome Teste,

Recebemos o seu cadastro no Sistema Nacional de Cultura.
Por favor confirme seu e-mail clicando no endereço abaixo:

http://snc.cultura.gov.br/adesao/ativar/usuario/{usuario.codigo_ativacao}

Atenciosamente,

Equipe SNC
Secretaria Especial da Cultura / Ministério da Cidadania
"""

    assert len(mail.outbox) == 1
    assert (
        mail.outbox[0].subject
        == "Secretaria Especial da Cultura / Ministério da Cidadania - SNC - CREDENCIAIS DE ACESSO"
    )
    assert mail.outbox[0].from_email == "naoresponda@cultura.gov.br"
    assert mail.outbox[0].to == ["email@email.com", "email@pessoal.com"]
    assert mail.outbox[0].body == texto


def test_envio_email_em_nova_adesao(client):
    user = User.objects.create(username="teste", email="email@email.com")
    user.set_password("123456")
    user.save()
    usuario = mommy.make("Usuario", user=user, nome_usuario="teste", email_pessoal="email@pessoal.com")

    ente_federado = mommy.make("EnteFederado", cod_ibge=123456)

    client.login(username=user.username, password="123456")

    gestor = Gestor(cpf="590.328.900-26", rg="1234567", orgao_expeditor_rg="ssp", estado_expeditor=29,
        nome="nome", telefone_um="123456", email_institucional="email@email.com", email_pessoal="email@pes.com",
        tipo_funcionario=2)
    sede = Sede(cnpj="70.658.964/0001-07", endereco="endereco", complemento="complemento",
        cep="72430101", bairro="bairro", telefone_um="123456")

    url = reverse("adesao:cadastrar_sistema")

    response = client.post(
        url,
        {
            "ente_federado": ente_federado.pk,
            "cpf": gestor.cpf,
            "rg": gestor.rg,
            "nome": gestor.nome,
            "orgao_expeditor_rg": gestor.orgao_expeditor_rg,
            "estado_expeditor": 29,
            "telefone_um": gestor.telefone_um,
            "email_institucional": gestor.email_institucional,
            "email_pessoal": gestor.email_pessoal,
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

    sistema = SistemaCultura.sistema.get(ente_federado__cod_ibge=ente_federado.cod_ibge)

    texto = f"""Prezado Gestor,

Um novo ente federado acabou de se cadastrar e fazer a solicitação de nova adesão.
Segue abaixo os dados de contato do ente federado:

Dados do Ente Federado:
Cadastrador: {sistema.cadastrador.nome_usuario}
Nome do Prefeito: {sistema.gestor.nome}
Cidade: {sistema.ente_federado.nome}
Email Institucional: {sistema.gestor.email_institucional}
Telefone de Contato: {sistema.sede.telefone_um}
Link da Adesão: http://snc.cultura.gov.br/gestao/detalhar/{sistema.ente_federado.cod_ibge}

Equipe SNC
SECRETARIA ESPECIAL DA CULTURA / MINISTÉRIO DA CIDADANIA"""

    assert len(mail.outbox) == 1
    assert (
        mail.outbox[0].subject
        == "SECRETARIA ESPECIAL DA CULTURA / MINISTÉRIO DA CIDADANIA - SNC - SOLICITAÇÃO NOVA ADESÃO"
    )
    assert mail.outbox[0].from_email == "naoresponda@cultura.gov.br"
    assert mail.outbox[0].to == [user.email, usuario.email_pessoal, sistema.gestor.email_pessoal,
        sistema.gestor.email_institucional]
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


def test_cadastrar_funcionario_tipo_gestor_cultura(login, client):

    sistema_cultura = mommy.make("SistemaCultura", _fill_optional=['ente_federado',
        'gestor', 'sede'], cadastrador=login, ente_federado__cod_ibge=123456)

    funcionario = Funcionario(cpf="381.390.630-29", rg="48.464.068-9",
        orgao_expeditor_rg="SSP", estado_expeditor=29,
        nome="Joao silva", email_institucional="joao@email.com")

    url = reverse("adesao:home")
    client.get(url)

    url = reverse("adesao:cadastrar_funcionario",
        kwargs={"sistema": sistema_cultura.id})

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

    assert sistema_cultura_atualizado.gestor_cultura == funcionario_salvo
    assert funcionario_salvo.cpf == funcionario.cpf
    assert funcionario_salvo.rg == funcionario.rg
    assert funcionario_salvo.orgao_expeditor_rg == funcionario.orgao_expeditor_rg
    assert funcionario_salvo.estado_expeditor == funcionario.estado_expeditor
    assert funcionario_salvo.nome == funcionario.nome
    assert funcionario_salvo.email_institucional == funcionario.email_institucional
    assert funcionario_salvo.tipo_funcionario == 0
    session = {}
    session['sistema_cultura_selecionado'] = model_to_dict(sistema_cultura_atualizado,
        exclude=['data_criacao', 'alterado_em', 'data_publicacao_acordo'])
    session['sistema_cultura_selecionado']['alterado_em'] = sistema_cultura_atualizado.alterado_em.strftime(
        "%d/%m/%Y às %H:%M:%S")
    session['sistema_cultura_selecionado']['alterado_por'] = sistema_cultura_atualizado.alterado_por.user.username
    assert client.session['sistema_cultura_selecionado'] == session['sistema_cultura_selecionado']
    assert client.session['sistema_gestor_cultura'] == model_to_dict(sistema_cultura_atualizado.gestor_cultura)


def test_alterar_funcionario_tipo_secretario(login, client):

    gestor_cultura = mommy.make("Funcionario", tipo_funcionario=0)
    sistema_cultura = mommy.make("SistemaCultura", gestor_cultura=gestor_cultura,
        _fill_optional=['ente_federado', 'sede', 'gestor'], ente_federado__cod_ibge=123456)

    url = reverse("adesao:alterar_funcionario",
        kwargs={"pk": sistema_cultura.gestor_cultura.id})

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

    assert sistema_cultura_atualizado.gestor_cultura.cpf == funcionario.cpf
    assert sistema_cultura_atualizado.gestor_cultura.rg == funcionario.rg
    assert sistema_cultura_atualizado.gestor_cultura.orgao_expeditor_rg == funcionario.orgao_expeditor_rg
    assert sistema_cultura_atualizado.gestor_cultura.estado_expeditor == funcionario.estado_expeditor
    assert sistema_cultura_atualizado.gestor_cultura.nome == funcionario.nome
    assert sistema_cultura_atualizado.gestor_cultura.email_institucional == funcionario.email_institucional
    assert sistema_cultura_atualizado.gestor_cultura.tipo_funcionario == 0

def test_cadastrar_funcionario_dados_invalidos(login, client):

    sistema_cultura = mommy.make("SistemaCultura", ente_federado__cod_ibge=123456)

    url = reverse("adesao:cadastrar_funcionario",
        kwargs={"sistema": sistema_cultura.id})

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
        'sede', 'gestor'], cadastrador=login, ente_federado__cod_ibge=123456)

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
    sistema_salvo = SistemaCultura.sistema.get(ente_federado=ente_federado)

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
        'gestor', 'sede'], gestor__tipo_funcionario=0, cadastrador=login,
        ente_federado__cod_ibge=123456)

    url = reverse("adesao:home")
    response = client.get(url)

    assert client.session['sistema_situacao'] == sistema.get_estado_processo_display()
    assert client.session['sistema_sede'] == model_to_dict(sistema.sede)
    assert client.session['sistema_gestor'] == model_to_dict(sistema.gestor, exclude=['termo_posse', 'rg_copia', 'cpf_copia'])
    assert client.session['sistema_ente'] == model_to_dict(sistema.ente_federado, fields=['nome', 'cod_ibge'])
    session = {}
    session['sistema_cultura_selecionado'] = model_to_dict(sistema,
        exclude=['data_criacao', 'alterado_em', 'data_publicacao_acordo'])
    session['sistema_cultura_selecionado']['alterado_em'] = sistema.alterado_em.strftime(
        "%d/%m/%Y às %H:%M:%S")
    assert client.session['sistema_cultura_selecionado'] == session['sistema_cultura_selecionado']

def test_session_user_com_mais_de_um_sistema_cultura(login, client):

    sistema_1 = mommy.make("SistemaCultura", _fill_optional=['ente_federado', 'secretario', 'responsavel'],
        ente_federado__nome='Acre', ente_federado__cod_ibge=12345, cadastrador=login)
    sistema_2 = mommy.make("SistemaCultura", _fill_optional=['ente_federado', 'secretario', 'responsavel'],
       ente_federado__nome='Brasília', ente_federado__cod_ibge=12346, cadastrador=login)

    url = reverse("adesao:home")
    response = client.get(url)

    assert 'sistema_cultura_selecionado' not in client.session
    assert client.session['sistemas'][0]['id'] == sistema_1.id
    assert client.session['sistemas'][0]['ente_federado__nome'] == sistema_1.ente_federado.nome
    assert client.session['sistemas'][1]['id'] == sistema_2.id
    assert client.session['sistemas'][1]['ente_federado__nome'] == sistema_2.ente_federado.nome
    assert len(client.session['sistemas']) == 2


def test_detalhar_conselheiros(client):
    sistema_cultura = mommy.make("SistemaCultura", _fill_optional=['conselho', 'ente_federado'],
        ente_federado__cod_ibge=123456)
    conselheiro = mommy.make("Conselheiro", conselho=sistema_cultura.conselho)

    url = reverse("adesao:detalhar", kwargs={'cod_ibge': sistema_cultura.ente_federado.cod_ibge})
    response = client.get(url)

    assert response.context_data['conselheiros'][0] == conselheiro


def test_home_apos_cadastro_de_gestor_de_cultura(client, login):
    sistema_cultura = mommy.make("SistemaCultura", ente_federado__cod_ibge=123456,
        _fill_optional=['gestor_cultura', 'gestor', 'sede'])

    url = reverse("adesao:define_sistema_sessao")
    client.post(url, data={"sistema": sistema_cultura.id})

    url = reverse("adesao:home")
    client.get(url)

    sistema_cultura_atualizado = SistemaCultura.sistema.get(
        ente_federado__cod_ibge=sistema_cultura.ente_federado.cod_ibge)

    texto = f"""{sistema_cultura_atualizado.ente_federado.nome}, sua Solicitação de Adesão ao Sistema Nacional de Cultura foi recebida em nosso sistema.
Para efetivar seu processo de adesão é necessário o envio dos documentos listados abaixo,
devidamente assinados pelo(a) Sr(a) {sistema_cultura_atualizado.gestor.nome}.

Documentos:
- 1 (uma) via do formulário de Solicitação de Integração ao SNC.
- 2 (duas) vias do Acordo de Cooperação Federativa.
Os documentos devem ser enviados à SAI/Minc pelos correios para o seguinte endereço:

Equipe SNC

Coordenação-Geral do SNC - CGSNC
SDC / Secretaria Especial da Cultura / Ministério da Cidadania
SCS Q. 09, Lote C, Bloco B, 10º andar
Edifício Parque Cidade Corporate
CEP: 70.308-200    Brasília-DF
E-mail: snc@cultura.gov.br

Seu prazo para o envio é de até 60 dias corridos.
"""

    assert sistema_cultura_atualizado.estado_processo == '1'
    session = {}
    session['sistema_cultura_selecionado'] = model_to_dict(sistema_cultura_atualizado,
        exclude=['data_criacao', 'alterado_em', 'data_publicacao_acordo'])
    session['sistema_cultura_selecionado']['alterado_em'] = sistema_cultura_atualizado.alterado_em.strftime(
        "%d/%m/%Y às %H:%M:%S")
    session['sistema_cultura_selecionado']['alterado_por'] = sistema_cultura_atualizado.alterado_por.user.username
    assert client.session['sistema_cultura_selecionado'] == session['sistema_cultura_selecionado']
    assert len(mail.outbox) == 1
    assert (
        mail.outbox[0].subject
        == "Sistema Nacional de Cultura - Solicitação de Adesão ao SNC"
    )
    assert mail.outbox[0].from_email == "naoresponda@cultura.gov.br"
    assert mail.outbox[0].to == [login.user.email, login.email_pessoal,
        sistema_cultura_atualizado.gestor.email_institucional,
        sistema_cultura_atualizado.gestor.email_pessoal]
    assert mail.outbox[0].body == texto


def test_home_apos_cadastro_de_gestor_de_cultura_sem_email_gestor(client, login):
    sistema_cultura = mommy.make("SistemaCultura", ente_federado__cod_ibge=123456,
        _fill_optional=['gestor_cultura', 'sede'])

    url = reverse("adesao:define_sistema_sessao")
    client.post(url, data={"sistema": sistema_cultura.id})

    url = reverse("adesao:home")
    client.get(url)

    sistema_cultura_atualizado = SistemaCultura.sistema.get(
        ente_federado__cod_ibge=sistema_cultura.ente_federado.cod_ibge)

    texto = f"""{sistema_cultura_atualizado.ente_federado.nome}, sua Solicitação de Adesão ao Sistema Nacional de Cultura foi recebida em nosso sistema.
Para efetivar seu processo de adesão é necessário o envio dos documentos listados abaixo,
devidamente assinados pelo(a) Sr(a) .

Documentos:
- 1 (uma) via do formulário de Solicitação de Integração ao SNC.
- 2 (duas) vias do Acordo de Cooperação Federativa.
Os documentos devem ser enviados à SAI/Minc pelos correios para o seguinte endereço:

Equipe SNC

Coordenação-Geral do SNC - CGSNC
SDC / Secretaria Especial da Cultura / Ministério da Cidadania
SCS Q. 09, Lote C, Bloco B, 10º andar
Edifício Parque Cidade Corporate
CEP: 70.308-200    Brasília-DF
E-mail: snc@cultura.gov.br

Seu prazo para o envio é de até 60 dias corridos.
"""

    assert sistema_cultura_atualizado.estado_processo == '1'
    session = {}
    session['sistema_cultura_selecionado'] = model_to_dict(sistema_cultura_atualizado,
        exclude=['data_criacao', 'alterado_em', 'data_publicacao_acordo'])
    session['sistema_cultura_selecionado']['alterado_em'] = sistema_cultura_atualizado.alterado_em.strftime(
        "%d/%m/%Y às %H:%M:%S")
    session['sistema_cultura_selecionado']['alterado_por'] = sistema_cultura_atualizado.alterado_por.user.username
    assert client.session['sistema_cultura_selecionado'] == session['sistema_cultura_selecionado']
    assert len(mail.outbox) == 1
    assert (
        mail.outbox[0].subject
        == "Sistema Nacional de Cultura - Solicitação de Adesão ao SNC"
    )
    assert mail.outbox[0].from_email == "naoresponda@cultura.gov.br"
    assert mail.outbox[0].to == [login.user.email, login.email_pessoal]
    assert mail.outbox[0].body == texto


def test_alterar_sistema_cultura(login, client):
    ente_federado = mommy.make("EnteFederado", cod_ibge=20563)
    gestor = Gestor(cpf="590.328.900-26", rg="1234567", orgao_expeditor_rg="ssp", estado_expeditor=29,
        nome="nome", telefone_um="123456", email_institucional="email@email.com", tipo_funcionario=2)
    sede = Sede(cnpj="70.658.964/0001-07", endereco="endereco", complemento="complemento",
        cep="72430101", bairro="bairro", telefone_um="123456")

    sistema_cultura = mommy.make("SistemaCultura", _fill_optional=['ente_federado'], cadastrador=login,
        ente_federado__cod_ibge=123456)

    url = reverse("adesao:home")
    client.get(url)

    url = reverse("adesao:alterar_sistema", kwargs={"pk": sistema_cultura.id})

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
    sistema_salvo = SistemaCultura.sistema.get(ente_federado=ente_federado)

    assert sistema_salvo.ente_federado.cod_ibge == ente_federado.cod_ibge
    assert sistema_salvo.gestor == gestor_salvo
    assert sistema_salvo.sede == sede_salva
    assert sistema_salvo.cadastrador == login


def test_atualizacao_relacoes_reversas(login, client):
    sistema_cultura = mommy.make("SistemaCultura", _fill_optional=['ente_federado'], cadastrador=login,
        ente_federado__cod_ibge=205631)

    url = reverse("adesao:home")
    client.get(url)

    mommy.make("Contato", sistema_cultura=sistema_cultura, _quantity=5)

    sistema_antigo = SistemaCultura.sistema.get(ente_federado__cod_ibge=205631)
    contatos = sistema_cultura.contatos

    sistema_cultura.estado_processo = 6
    sistema_cultura.save()

    sistema_cultura_atualizado = SistemaCultura.sistema.get(ente_federado__cod_ibge=205631)

    assert not sistema_antigo.contatos.all()
    assert sistema_cultura_atualizado.contatos == contatos
