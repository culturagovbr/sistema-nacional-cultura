import pytest

from model_mommy import mommy

from django.shortcuts import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from dal.autocomplete import ModelSelect2

from adesao.forms import CadastrarMunicipioForm, CadastrarSistemaCulturaForm, CadastrarGestor, CadastrarSede
from adesao.models import Usuario


@pytest.fixture
def cadastrar_municipio_form(login):
    user = Usuario.objects.first()
    kwargs = {'user': user}
    return CadastrarMunicipioForm(**kwargs)


def test_widget_estado_form_cadastrar_municipio(client, cadastrar_municipio_form):
    """
    Testa o uso do widget ModelSelect2 na campo estado no form de
    cadastrar município
    """

    form = cadastrar_municipio_form
    assert isinstance(form['estado'].field.widget, ModelSelect2)


def test_url_widget_estado_form_cadastrar_municipio(client, cadastrar_municipio_form):
    """
    Testa url usada pelo widget ModelSelect2 no campo estado no form
    de cadastrar municipio
    """

    form = cadastrar_municipio_form
    uf_url = reverse('gestao:uf_chain')

    assert form['estado'].field.widget.url == uf_url


def test_widget_cidade_form_cadastrar_municipio(client, cadastrar_municipio_form):
    """
    Testa o uso do widget ModelSelect2 no campo cidade no form de
    cadastrar municipio
    """

    form = cadastrar_municipio_form
    assert isinstance(form['cidade'].field.widget, ModelSelect2)


def test_url_widget_cidade_form_cadastrar_municipio(client, cadastrar_municipio_form):
    """
    Testa url usada pelo widget ModelSelect2 no campo cidade no
    form de cadastrar municipio
    """

    form = cadastrar_municipio_form
    municipio_url = reverse('gestao:cidade_chain')
    assert form['cidade'].field.widget.url == municipio_url


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

    form = CadastrarGestor(data=data, files={"termo_posse": SimpleUploadedFile(
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

    form = CadastrarGestor(data=data, files={"termo_posse": SimpleUploadedFile(
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


def test_save_cadastrar_sede_dados_validos(client, login, sistema_cultura):
    """ Testa se a função is_valid retorna verdadeiro para a criação de uma sede com
    dados validos"""

    data = {'cnpj': '93.308.686/0001-63',
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
