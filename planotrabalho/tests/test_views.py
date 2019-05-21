import pytest
import datetime

from django.shortcuts import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from adesao.models import SistemaCultura
from planotrabalho.models import Componente
from planotrabalho.models import FundoDeCultura
from planotrabalho.models import Conselheiro
from planotrabalho.models import ConselhoDeCultura

from model_mommy import mommy


def test_cadastrar_componente_tipo_legislacao(client, login):

    sistema_cultura = mommy.make("SistemaCultura", _fill_optional=['ente_federado', 'sede', 'gestor'],
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

    sistema_cultura = mommy.make("SistemaCultura", _fill_optional=['ente_federado', 'sede', 'gestor'],
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

    sistema_cultura = mommy.make("SistemaCultura", _fill_optional=['ente_federado', 'sede', 'gestor'],
        cadastrador=login)

    url = reverse("adesao:home")
    client.get(url)

    url = reverse("planotrabalho:cadastrar_componente", kwargs={"tipo": "fundo_cultura"})

    arquivo = SimpleUploadedFile(
        "componente.txt", b"file_content", content_type="text/plain"
    )
    cnpj = SimpleUploadedFile(
        "cnpj.txt", b"file_content", content_type="text/plain"
    )
    response = client.post(url, data={"arquivo": arquivo,
                                      "data_publicacao": '28/06/2018',
                                      "possui_cnpj": 'True',
                                      "cnpj": '75.336.659/0001-12',
                                      'mesma_lei': 'False',
                                      "comprovante": cnpj})

    sistema_atualizado = SistemaCultura.sistema.get(
        ente_federado__nome=sistema_cultura.ente_federado.nome)

    assert response.status_code == 302
    assert arquivo.name.split(".")[0] in sistema_atualizado.fundo_cultura.arquivo.name.split("/")[-1]
    assert sistema_atualizado.fundo_cultura.data_publicacao == datetime.date(2018, 6, 28)
    assert sistema_atualizado.fundo_cultura.tipo == 2


def test_cadastrar_componente_tipo_fundo_cultura_reaproveita_lei_sem_cnpj(client, login):

    sistema_cultura = mommy.make("SistemaCultura", _fill_optional=['ente_federado', 'sede', 'gestor', 'legislacao'],
        cadastrador=login)
    legislacao = SimpleUploadedFile(
        "legislacao.txt", b"file_content", content_type="text/plain"
    )
    sistema_cultura.legislacao.arquivo = legislacao
    sistema_cultura.legislacao.save()

    url = reverse("adesao:home")
    client.get(url)

    url = reverse("planotrabalho:cadastrar_componente", kwargs={"tipo": "fundo_cultura"})

    response = client.post(url, data={"possui_cnpj": 'False',
                                      'mesma_lei': 'True'})

    sistema_atualizado = SistemaCultura.sistema.get(
        ente_federado__nome=sistema_cultura.ente_federado.nome)

    assert response.status_code == 302
    assert sistema_atualizado.legislacao.arquivo.name.split("/")[-1] in sistema_atualizado.fundo_cultura.arquivo.name.split("/")[-1]
    assert sistema_atualizado.legislacao.data_publicacao == sistema_atualizado.fundo_cultura.data_publicacao
    assert sistema_atualizado.fundo_cultura.tipo == 2


def test_cadastrar_componente_tipo_fundo_cultura_reaproveita_lei_com_cnpj(client, login):

    sistema_cultura = mommy.make("SistemaCultura", _fill_optional=['ente_federado', 'sede', 'gestor', 'legislacao'],
        cadastrador=login)
    legislacao = SimpleUploadedFile(
        "legislacao_teste.txt", b"file_content", content_type="text/plain"
    )
    sistema_cultura.legislacao.arquivo = legislacao
    sistema_cultura.legislacao.save()

    url = reverse("adesao:home")
    client.get(url)

    url = reverse("planotrabalho:cadastrar_componente", kwargs={"tipo": "fundo_cultura"})

    cnpj = SimpleUploadedFile(
        "cnpj.txt", b"file_content", content_type="text/plain"
    )
    response = client.post(url, data={"possui_cnpj": 'True',
                                      "cnpj": '75.336.659/0001-12',
                                      "comprovante": cnpj,
                                      'mesma_lei': 'True'})

    sistema_atualizado = SistemaCultura.sistema.get(
        ente_federado__nome=sistema_cultura.ente_federado.nome)

    assert response.status_code == 302
    assert sistema_atualizado.legislacao.arquivo.name.split("/")[-1] in sistema_atualizado.fundo_cultura.arquivo.name.split("/")[-1]
    assert sistema_atualizado.legislacao.data_publicacao == sistema_atualizado.fundo_cultura.data_publicacao
    assert cnpj.name.split(".")[0] in sistema_atualizado.fundo_cultura.comprovante_cnpj.arquivo.name.split("/")[-1]
    assert sistema_atualizado.fundo_cultura.cnpj == '75.336.659/0001-12'
    assert sistema_atualizado.fundo_cultura.tipo == 2


def test_cadastrar_componente_tipo_conselho(client, login):

    sistema_cultura = mommy.make("SistemaCultura", _fill_optional=['ente_federado', 'sede', 'gestor'],
        cadastrador=login)

    url = reverse("adesao:home")
    client.get(url)

    url = reverse("planotrabalho:cadastrar_componente", kwargs={"tipo": "conselho"})

    arquivo_ata = SimpleUploadedFile(
        "ata.txt", b"file_content", content_type="text/plain"
    )
    arquivo_lei = SimpleUploadedFile(
        "lei.txt", b"file_content", content_type="text/plain"
    )
    response = client.post(url, data={'mesma_lei': False,
                                      'arquivo': arquivo_ata,
                                      'data_publicacao': '28/06/2018',
                                      'arquivo_lei': arquivo_lei,
                                      'data_publicacao_lei': '29/06/2018',
                                      'possui_ata': True,
                                      'paritario': True,
                                      'exclusivo_cultura': True})

    sistema_atualizado = SistemaCultura.sistema.get(
        ente_federado__nome=sistema_cultura.ente_federado.nome)

    assert response.status_code == 302
    assert arquivo_ata.name.split(".")[0] in sistema_atualizado.conselho.arquivo.name.split("/")[-1]
    assert arquivo_lei.name.split(".")[0] in sistema_atualizado.conselho.lei.arquivo.name.split("/")[-1]
    assert sistema_atualizado.conselho.data_publicacao == datetime.date(2018, 6, 28)
    assert sistema_atualizado.conselho.lei.data_publicacao == datetime.date(2018, 6, 29)
    assert sistema_atualizado.conselho.tipo == 3


def test_cadastrar_componente_tipo_conselho_importar_lei(client, login):

    sistema_cultura = mommy.make("SistemaCultura", _fill_optional=['ente_federado', 'sede', 'gestor', 'legislacao'],
        cadastrador=login)
    legislacao = SimpleUploadedFile(
        "legislacao.txt", b"file_content", content_type="text/plain"
    )
    sistema_cultura.legislacao.arquivo = legislacao
    sistema_cultura.legislacao.save()

    url = reverse("adesao:home")
    client.get(url)

    url = reverse("planotrabalho:cadastrar_componente", kwargs={"tipo": "conselho"})

    response = client.post(url, data={'mesma_lei': True,
                                      'possui_ata': False,
                                      'paritario': True,
                                      'exclusivo_cultura': True})

    sistema_atualizado = SistemaCultura.sistema.get(
        ente_federado__nome=sistema_cultura.ente_federado.nome)

    assert response.status_code == 302
    assert sistema_atualizado.legislacao.arquivo.name.split("/")[-1] in sistema_atualizado.conselho.lei.arquivo.name.split("/")[-1]
    assert sistema_atualizado.legislacao.data_publicacao == sistema_atualizado.conselho.lei.data_publicacao
    assert sistema_atualizado.conselho.paritario 
    assert sistema_atualizado.conselho.exclusivo_cultura
    assert sistema_atualizado.conselho.tipo == 3


def test_cadastrar_componente_tipo_plano(client, login):

    sistema_cultura = mommy.make("SistemaCultura", _fill_optional=['ente_federado', 'sede', 'gestor'],
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

    sistema_cultura = mommy.make("SistemaCultura", _fill_optional=['ente_federado', 'legislacao', 'sede', 'gestor'],
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

    sistema_cultura = mommy.make("SistemaCultura", _fill_optional=['ente_federado', 'fundo_cultura', 'sede', 'gestor'],
        cadastrador=login)

    url = reverse("adesao:home")
    client.get(url)

    url = reverse("planotrabalho:alterar_fundo", kwargs={"pk": sistema_cultura.fundo_cultura.id})

    numero_componentes = Componente.objects.count()
    numero_fundo_cultura = FundoDeCultura.objects.count()

    arquivo = SimpleUploadedFile(
        "novo.txt", b"file_content", content_type="text/plain"
    )
    response = client.post(url, data={"mesma_lei": "False",
                                      "possui_cnpj": "Sim",
                                      "arquivo": arquivo,
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


def test_alterar_fundo_cultura_remove_cnpj(client, login):
    arquivo = SimpleUploadedFile(
        "novo.txt", b"file_content", content_type="text/plain"
    )
    comprovante = SimpleUploadedFile(
        "comprovante.txt", b"file_content", content_type="text/plain"
    )

    sistema_cultura = mommy.make("SistemaCultura", _fill_optional=['ente_federado', 'fundo_cultura', 'sede', 'gestor'],
        cadastrador=login)
    sistema_cultura.fundo_cultura.cnpj = "56.385.239/0001-81"
    sistema_cultura.fundo_cultura.comprovante_cnpj = mommy.make("ArquivoComponente2")
    sistema_cultura.fundo_cultura.save()

    url = reverse("adesao:home")
    client.get(url)

    url = reverse("planotrabalho:alterar_fundo", kwargs={"pk": sistema_cultura.fundo_cultura.id})

    numero_componentes = Componente.objects.count()
    numero_fundo_cultura = FundoDeCultura.objects.count()

    response = client.post(url, data={"mesma_lei": "False",
                                      "possui_cnpj": "False",
                                      "arquivo": arquivo,
                                      "data_publicacao": "25/06/2018",
                                      "cnpj": "56.385.239/0001-81",
                                      "comprovante": comprovante})

    sistema_atualizado = SistemaCultura.sistema.get(
        ente_federado__nome=sistema_cultura.ente_federado.nome)

    numero_componentes_apos_update = Componente.objects.count()
    numero_fundo_cultura_apos_update = FundoDeCultura.objects.count()

    assert numero_fundo_cultura == numero_fundo_cultura_apos_update
    assert numero_componentes == numero_componentes_apos_update
    assert response.status_code == 302
    assert arquivo.name.split(".")[0] in sistema_atualizado.fundo_cultura.arquivo.name.split("/")[-1]
    assert sistema_atualizado.fundo_cultura.data_publicacao == datetime.date(2018, 6, 25)
    assert sistema_atualizado.fundo_cultura.cnpj == None
    assert sistema_atualizado.fundo_cultura.comprovante_cnpj == None
    assert sistema_atualizado.fundo_cultura.tipo == 2


def test_alterar_conselho_cultura(client, login):

    componente = mommy.make("ConselhoDeCultura", tipo=3, _fill_optional=True)
    sistema_cultura = mommy.make("SistemaCultura", _fill_optional=['ente_federado', 'sede', 'gestor'],
        cadastrador=login, conselho=componente)

    url = reverse("adesao:home")
    client.get(url)

    url = reverse("planotrabalho:alterar_conselho", kwargs={"pk": sistema_cultura.conselho.id})

    numero_componentes = Componente.objects.count()
    numero_conselho_cultura = ConselhoDeCultura.objects.count()

    arquivo_lei = SimpleUploadedFile(
        "novo_lei.txt", b"file_content", content_type="text/plain"
    )
    arquivo_ata = SimpleUploadedFile(
        "novo_ata.txt", b"file_content", content_type="text/plain"
    )
    response = client.post(url, data={"mesma_lei": False,
                                      "arquivo": arquivo_ata,
                                      "data_publicacao": "25/06/2018",
                                      "arquivo_lei": arquivo_lei,
                                      "data_publicacao_lei": "26/06/2018",
                                      'possui_ata': True,
                                      'exclusivo_cultura': True,
                                      'paritario': True})

    sistema_atualizado = SistemaCultura.sistema.get(
        ente_federado__nome=sistema_cultura.ente_federado.nome)

    numero_componentes_apos_update = Componente.objects.count()
    numero_conselho_cultura_apos_update = ConselhoDeCultura.objects.count()

    assert numero_conselho_cultura == numero_conselho_cultura_apos_update
    assert numero_componentes == numero_componentes_apos_update
    assert response.status_code == 302
    assert arquivo_ata.name.split(".")[0] in sistema_atualizado.conselho.arquivo.name.split("/")[-1]
    assert arquivo_lei.name.split(".")[0] in sistema_atualizado.conselho.lei.arquivo.name.split("/")[-1]
    assert sistema_atualizado.conselho.data_publicacao == datetime.date(2018, 6, 25)
    assert sistema_atualizado.conselho.lei.data_publicacao == datetime.date(2018, 6, 26)
    assert sistema_atualizado.conselho.tipo == 3


def teste_criar_conselheiro(client, login):

    sistema = mommy.make("SistemaCultura", _fill_optional=['ente_federado', 'conselho', 'sede', 'gestor'], 
        cadastrador=login)

    url = reverse("adesao:home")
    client.get(url)

    url = reverse("planotrabalho:criar_conselheiro", kwargs={'conselho': sistema.conselho.id})
    response = client.post(url, data={"nome": "teste",
        "segmento": "20", "email": "email@email.com"})

    conselheiro = Conselheiro.objects.last()

    assert conselheiro.nome == "teste"
    assert conselheiro.segmento == "Teatro"
    assert conselheiro.email == "email@email.com"
    assert conselheiro.conselho == sistema.conselho


def teste_alterar_conselheiro(client, login):

    sistema = mommy.make("SistemaCultura", _fill_optional=['ente_federado', 'conselho', 'sede', 'gestor'], 
        cadastrador=login)
    conselheiro = mommy.make("Conselheiro", conselho=sistema.conselho)

    url = reverse("adesao:home")
    client.get(url)

    url = reverse("planotrabalho:alterar_conselheiro", kwargs={'pk': conselheiro.id})
    response = client.post(url, data={"nome": "teste",
        "segmento": "20", "email": "email@email.com"})

    conselheiro.refresh_from_db()

    assert conselheiro.nome == "teste"
    assert conselheiro.segmento == "Teatro"
    assert conselheiro.email == "email@email.com"
    assert conselheiro.conselho == sistema.conselho


def teste_remover_conselheiro(client, login):

    sistema = mommy.make("SistemaCultura", _fill_optional=['ente_federado', 'conselho', 'sede', 'gestor'], 
        cadastrador=login)
    conselheiro = mommy.make("Conselheiro", conselho=sistema.conselho)

    url = reverse("adesao:home")
    client.get(url)

    url = reverse("planotrabalho:remover_conselheiro", kwargs={'pk': conselheiro.id})
    
    response = client.post(url)

    conselheiro.refresh_from_db()

    assert conselheiro.situacao == '0'
