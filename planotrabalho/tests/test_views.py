import pytest
import datetime

from django.shortcuts import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from adesao.models import SistemaCultura
from planotrabalho.models import Componente
from planotrabalho.models import FundoDeCultura

from model_mommy import mommy


def test_cadastrar_componente_tipo_legislacao(client, login):

    sistema_cultura = mommy.make("SistemaCultura", _fill_optional=['ente_federado'],
        cadastrador=login)

    url = reverse("adesao:home")
    client.get(url)

    url = reverse("planotrabalho:cadastrar_componente", kwargs={"tipo": "legislacao"})

    arquivo = SimpleUploadedFile(
        "componente.txt", b"file_content", content_type="text/plain"
    )
    response = client.post(url, data={"arquivo": arquivo,
                                      'data_publicacao': '28/06/2018'})

    sistema_atualizado = SistemaCultura.sistema.get(
        ente_federado__nome=sistema_cultura.ente_federado.nome)

    assert response.status_code == 302
    assert arquivo.name.split(".")[0] in sistema_atualizado.legislacao.arquivo.name.split("/")[-1]
    assert sistema_atualizado.legislacao.data_publicacao == datetime.date(2018, 6, 28)
    assert sistema_atualizado.legislacao.tipo == 0


def test_cadastrar_componente_tipo_orgao_gestor(client, login):

    sistema_cultura = mommy.make("SistemaCultura", _fill_optional=['ente_federado'],
        cadastrador=login)

    url = reverse("adesao:home")
    client.get(url)

    url = reverse("planotrabalho:cadastrar_componente", kwargs={"tipo": "orgao_gestor"})

    arquivo = SimpleUploadedFile(
        "componente.txt", b"file_content", content_type="text/plain"
    )
    response = client.post(url, data={"arquivo": arquivo,
                                      'data_publicacao': '28/06/2018'})

    sistema_atualizado = SistemaCultura.sistema.get(
        ente_federado__nome=sistema_cultura.ente_federado.nome)

    assert response.status_code == 302
    assert arquivo.name.split(".")[0] in sistema_atualizado.orgao_gestor.arquivo.name.split("/")[-1]
    assert sistema_atualizado.orgao_gestor.data_publicacao == datetime.date(2018, 6, 28)
    assert sistema_atualizado.orgao_gestor.tipo == 1


def test_cadastrar_componente_tipo_fundo_cultura(client, login):

    sistema_cultura = mommy.make("SistemaCultura", _fill_optional=['ente_federado'],
        cadastrador=login)

    url = reverse("adesao:home")
    client.get(url)

    url = reverse("planotrabalho:cadastrar_componente", kwargs={"tipo": "fundo_cultura"})

    arquivo = SimpleUploadedFile(
        "componente.txt", b"file_content", content_type="text/plain"
    )
    response = client.post(url, data={"arquivo": arquivo,
                                      "data_publicacao": '28/06/2018',
                                      "cnpj": '75.336.659/0001-12'})

    sistema_atualizado = SistemaCultura.sistema.get(
        ente_federado__nome=sistema_cultura.ente_federado.nome)

    assert response.status_code == 302
    assert arquivo.name.split(".")[0] in sistema_atualizado.fundo_cultura.arquivo.name.split("/")[-1]
    assert sistema_atualizado.fundo_cultura.data_publicacao == datetime.date(2018, 6, 28)
    assert sistema_atualizado.fundo_cultura.tipo == 2


def test_cadastrar_componente_tipo_conselho(client, login):

    sistema_cultura = mommy.make("SistemaCultura", _fill_optional=['ente_federado'],
        cadastrador=login)

    url = reverse("adesao:home")
    client.get(url)

    url = reverse("planotrabalho:cadastrar_componente", kwargs={"tipo": "conselho"})

    arquivo = SimpleUploadedFile(
        "componente.txt", b"file_content", content_type="text/plain"
    )
    response = client.post(url, data={"arquivo": arquivo,
                                      'data_publicacao': '28/06/2018'})

    sistema_atualizado = SistemaCultura.sistema.get(
        ente_federado__nome=sistema_cultura.ente_federado.nome)

    assert response.status_code == 302
    assert arquivo.name.split(".")[0] in sistema_atualizado.conselho.arquivo.name.split("/")[-1]
    assert sistema_atualizado.conselho.data_publicacao == datetime.date(2018, 6, 28)
    assert sistema_atualizado.conselho.tipo == 3


def test_cadastrar_componente_tipo_plano(client, login):

    sistema_cultura = mommy.make("SistemaCultura", _fill_optional=['ente_federado'],
        cadastrador=login)

    url = reverse("adesao:home")
    client.get(url)

    url = reverse("planotrabalho:cadastrar_componente", kwargs={"tipo": "plano"})

    arquivo = SimpleUploadedFile(
        "componente.txt", b"file_content", content_type="text/plain"
    )
    response = client.post(url, data={"arquivo": arquivo,
                                      'data_publicacao': '28/06/2018'})

    sistema_atualizado = SistemaCultura.sistema.get(
        ente_federado__nome=sistema_cultura.ente_federado.nome)

    assert response.status_code == 302
    assert arquivo.name.split(".")[0] in sistema_atualizado.plano.arquivo.name.split("/")[-1]
    assert sistema_atualizado.plano.data_publicacao == datetime.date(2018, 6, 28)
    assert sistema_atualizado.plano.tipo == 4


def test_alterar_componente(client, login):

    sistema_cultura = mommy.make("SistemaCultura", _fill_optional=['ente_federado', 'legislacao'],
        cadastrador=login)

    url = reverse("adesao:home")
    client.get(url)

    url = reverse("planotrabalho:alterar_componente", kwargs={"tipo": "legislacao", 
        "pk": sistema_cultura.legislacao.id})

    numero_componentes = Componente.objects.count()

    arquivo = SimpleUploadedFile(
        "novo.txt", b"file_content", content_type="text/plain"
    )
    response = client.post(url, data={"arquivo": arquivo,
                                      "data_publicacao": "25/06/2018"})

    sistema_atualizado = SistemaCultura.sistema.get(
        ente_federado__nome=sistema_cultura.ente_federado.nome)

    numero_componentes_apos_update = Componente.objects.count()

    assert numero_componentes == numero_componentes_apos_update
    assert response.status_code == 302
    assert arquivo.name.split(".")[0] in sistema_atualizado.legislacao.arquivo.name.split("/")[-1]
    assert sistema_atualizado.legislacao.data_publicacao == datetime.date(2018, 6, 25)
    assert sistema_atualizado.legislacao.tipo == 0


def test_alterar_fundo_cultura(client, login):

    sistema_cultura = mommy.make("SistemaCultura", _fill_optional=['ente_federado', 'fundo_cultura'],
        cadastrador=login)

    url = reverse("adesao:home")
    client.get(url)

    url = reverse("planotrabalho:alterar_fundo", kwargs={"pk": sistema_cultura.fundo_cultura.id})

    numero_componentes = Componente.objects.count()
    numero_fundo_cultura = FundoDeCultura.objects.count()

    arquivo = SimpleUploadedFile(
        "novo.txt", b"file_content", content_type="text/plain"
    )
    response = client.post(url, data={"arquivo": arquivo,
                                      "data_publicacao": "25/06/2018",
                                      "cnpj": "56.385.239/0001-81"})

    sistema_atualizado = SistemaCultura.sistema.get(
        ente_federado__nome=sistema_cultura.ente_federado.nome)

    numero_componentes_apos_update = Componente.objects.count()
    numero_fundo_cultura_apos_update = FundoDeCultura.objects.count()

    assert numero_fundo_cultura == numero_fundo_cultura_apos_update
    assert numero_componentes == numero_componentes_apos_update
    assert response.status_code == 302
    assert arquivo.name.split(".")[0] in sistema_atualizado.fundo_cultura.arquivo.name.split("/")[-1]
    assert sistema_atualizado.fundo_cultura.data_publicacao == datetime.date(2018, 6, 25)
    assert sistema_atualizado.fundo_cultura.cnpj == "56.385.239/0001-81"
    assert sistema_atualizado.fundo_cultura.tipo == 2
