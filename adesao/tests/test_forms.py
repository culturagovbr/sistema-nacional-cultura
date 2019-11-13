import pytest

from model_mommy import mommy

from django.shortcuts import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from dal.autocomplete import ModelSelect2

from adesao.forms import CadastrarSistemaCulturaForm, CadastrarGestor, CadastrarSede, CadastrarUsuarioForm
from adesao.models import Usuario


@pytest.fixture
def cadastrar_municipio_form(login):
    user = Usuario.objects.first()
    kwargs = {'user': user}
    return CadastrarMunicipioForm(**kwargs)


def test_widget_form_cadastrar_ente(client):
    """
    Testa o uso do widget ModelSelect2 na campo ente_federado no form de
    cadastrar sistema cultura
    """

    form = CadastrarSistemaCulturaForm()
    assert isinstance(form['ente_federado'].field.widget, ModelSelect2)


def test_url_widget_form_cadastrar_ente_url(client):
    """
    Testa url usada pelo widget ModelSelect2 no campo ente_federado no form
    de cadastrar sistema cultura
    """

    form = CadastrarSistemaCulturaForm()
    url = reverse('gestao:ente_chain')

    assert form['ente_federado'].field.widget.url == url


def test_save_cadastrar_sistema_cultura_dados_validos(client, login, sistema_cultura):
    """ Testa se a função is_valid retorna verdadeiro para a criação de um sistema cultura
    com dados válidos"""

    ente_federado = mommy.make("EnteFederado")

    data = {'ente_federado': ente_federado.pk }

    form = CadastrarSistemaCulturaForm(data=data)

    assert form.is_valid()


def test_save_cadastrar_sistema_cultura_ente_ja_cadastrado(client, login, sistema_cultura):
    """ Testa se a função is_valid retorna falso para a criação de um sistema cultura com
    um ente federado já cadastrado"""

    ente_federado = mommy.make("EnteFederado")
    sistema = mommy.make("SistemaCultura", ente_federado=ente_federado)

    data = {'ente_federado': ente_federado.pk }

    form = CadastrarSistemaCulturaForm(data=data)

    assert not form.is_valid()


def test_save_cadastrar_gestor_dados_validos(client, login, sistema_cultura):
    """ Testa se a função is_valid retorna verdadeiro para a criação de gestor com 
    dados validos"""

    data = {
            'cpf': '05447081130',
            'rg': '3643424',
            'nome': 'nome',
            'orgao_expeditor_rg': 'ssp',
            'estado_expeditor': 29,
            'telefone_um': '999999999',
            'email_institucional': 'email@email.com',
            'tipo_funcionario': 2, 
    }

    form = CadastrarGestor(data=data, logged_user=login.user, files={"termo_posse": SimpleUploadedFile(
                "test_file.pdf", bytes("test text", "utf-8")
            ),
            "cpf_copia": SimpleUploadedFile(
                "test_file2.pdf", bytes("test text", "utf-8")
            ),
            "rg_copia": SimpleUploadedFile(
                "test_file2.pdf", bytes("test text", "utf-8")
            )
        }
    )

    assert form.is_valid()


def test_save_cadastrar_gestor_cpf_invalido(client, login, sistema_cultura):
    """ Testa se a função is_valid retorna falso para a criação de gestor com 
    cpf invalido"""

    data = {'cpf': '123456',
            'rg': '3643424',
            'nome': 'nome',
            'orgao_expeditor_rg': 'ssp',
            'estado_expeditor': 29,
            'telefone_um': '999999999',
            'email_institucional': 'email@email.com',
            'tipo_funcionario': 2, 
    }

    form = CadastrarGestor(data=data, logged_user=login.user, files={"termo_posse": SimpleUploadedFile(
                "test_file.pdf", bytes("test text", "utf-8")
            ),
            "cpf_copia": SimpleUploadedFile(
                "test_file2.pdf", bytes("test text", "utf-8")
            ),
            "rg_copia": SimpleUploadedFile(
                "test_file2.pdf", bytes("test text", "utf-8")
            )
        }
    )

    assert not form.is_valid()


def test_save_cadastrar_sede_dados_validos(client, login, sistema_cultura, cnpj):
    """ Testa se a função is_valid retorna verdadeiro para a criação de uma sede com
    dados validos"""

    data = {'cnpj': '28.134.084/0001-75',
            'endereco': 'endereco',
            'complemento': 'complemento',
            'cep': '72430101',
            'bairro': 'bairro',
            'telefone_um': '999999999' }

    form = CadastrarSede(data=data)

    assert form.is_valid()


def test_save_cadastrar_sede_cnpj_invalido(client, login, sistema_cultura):
    """ Testa se a função is_valid retorna falso para a criação de uma sede com
    cnpj invalido"""

    data = {'cnpj': '123456',
            'endereco': 'endereco',
            'complemento': 'complemento',
            'cep': '72430101',
            'bairro': 'bairro',
            'telefone_um': '999999999' }

    form = CadastrarSede(data=data)

    assert not form.is_valid()


def test_save_cadastrar_usuario(client, login, sistema_cultura):
    """ Testa se a função is_valid retorna verdadeiro para a criação de um usuário"""

    data = {'username': '552.091.100-28',
            'email': 'email@email.com',
            'confirmar_email': 'email@email.com',
            'email_pessoal': 'email@pessoal.com',
            'confirmar_email_pessoal': 'email@pessoal.com',
            'nome_usuario': 'Teste',
            'password1': '123456',
            'password2': '123456'}

    form = CadastrarUsuarioForm(data=data)

    assert form.is_valid()


def test_save_cadastrar_usuario_email_ja_cadastrado(client, login, sistema_cultura):
    """ Testa se a função is_valid retorna falso para a criação de um usuário
    com um email já cadastrado"""

    usuario = Usuario.objects.first()

    data = {'username': '55209110028',
            'email': usuario.user.email,
            'confirmar_email': usuario.user.email,
            'nome_usuario': 'Teste',
            'password1': '123456', 
            'password2': '123456'}

    form = CadastrarUsuarioForm(data=data)

    assert not form.is_valid()


def test_save_cadastrar_usuario_email_pessoal_igual_institucional_ja_cadastrado(client, login, sistema_cultura):
    """ Testa se a função is_valid retorna falso para a criação de um usuário
    com um email pessoal igual a um email institucional já cadastrado"""

    usuario = Usuario.objects.exclude(user__email='').first()

    data = {'username': '55209110028',
            'email': 'email@email.com',
            'confirmar_email': 'email@email.com',
            'email_pessoal': usuario.user.email,
            'confirmar_email_pessoal': usuario.user.email,
            'nome_usuario': 'Teste',
            'password1': '123456', 
            'password2': '123456'}

    form = CadastrarUsuarioForm(data=data)

    assert not form.is_valid()


def test_save_cadastrar_usuario_email_pessoal_igual_pessoal_ja_cadastrado(client, login, sistema_cultura):
    """ Testa se a função is_valid retorna falso para a criação de um usuário
    com um email pessoal já cadastrado"""

    usuario = Usuario.objects.first()
    usuario.email_pessoal = 'email_pessoal@email.com'
    usuario.save()

    data = {'username': '55209110028',
            'email': 'email@email.com',
            'confirmar_email': 'email@email.com',
            'email_pessoal': usuario.email_pessoal,
            'confirmar_email_pessoal': usuario.email_pessoal,
            'nome_usuario': 'Teste',
            'password1': '123456', 
            'password2': '123456'}

    form = CadastrarUsuarioForm(data=data)

    assert not form.is_valid()


def test_save_cadastrar_usuario_email_pessoal_diferente_confirmacao(client, login, sistema_cultura):
    """ Testa se a função is_valid retorna falso para a criação de um usuário
    com um email pessoal diferente da confirmação de email pessoal"""

    data = {'username': '55209110028',
            'email': 'email@email.com',
            'confirmar_email': 'email@email.com',
            'email_pessoal': 'email@pessoal.com',
            'confirmar_email_pessoal': 'email@a.com',
            'nome_usuario': 'Teste',
            'password1': '123456', 
            'password2': '123456'}

    form = CadastrarUsuarioForm(data=data)

    assert not form.is_valid()
