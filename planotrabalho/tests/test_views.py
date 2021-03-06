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
        cadastrador=login, ente_federado__cod_ibge=123456)

    url = reverse("adesao:home")
    client.get(url)

    url = reverse("planotrabalho:cadastrar_legislacao")

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
        cadastrador=login, ente_federado__cod_ibge=123456)

    url = reverse("adesao:home")
    client.get(url)

    url = reverse("planotrabalho:cadastrar_orgao")

    arquivo = SimpleUploadedFile(
        "componente.txt", b"file_content", content_type="text/plain"
    )
    response = client.post(url, data={"arquivo": arquivo,
                                      'data_publicacao': '28/06/2018',
                                      'perfil': 0})

    sistema_atualizado = SistemaCultura.sistema.get(
        ente_federado__nome=sistema_cultura.ente_federado.nome)

    assert response.status_code == 302
    assert arquivo.name.split(".")[0] in sistema_atualizado.orgao_gestor.arquivo.name.split("/")[-1]
    assert sistema_atualizado.orgao_gestor.data_publicacao == datetime.date(2018, 6, 28)
    assert sistema_atualizado.orgao_gestor.perfil == 0
    assert sistema_atualizado.orgao_gestor.tipo == 1


def test_alterar_orgao_gestor(client, login):

    sistema_cultura = mommy.make("SistemaCultura", _fill_optional=['ente_federado', 'orgao_gestor', 'sede', 'gestor'],
        cadastrador=login, ente_federado__cod_ibge=123456)

    url = reverse("adesao:home")
    client.get(url)

    url = reverse("planotrabalho:alterar_orgao", kwargs={"pk": sistema_cultura.orgao_gestor.id})

    arquivo = SimpleUploadedFile(
        "novo.txt", b"file_content", content_type="text/plain"
    )
    response = client.post(url, data={"arquivo": arquivo,
                                      "data_publicacao": "25/06/2018",
                                      "perfil": 0})

    sistema_atualizado = SistemaCultura.sistema.get(
        ente_federado__nome=sistema_cultura.ente_federado.nome)

    assert arquivo.name.split(".")[0] in sistema_atualizado.orgao_gestor.arquivo.name.split("/")[-1]
    assert sistema_atualizado.orgao_gestor.data_publicacao == datetime.date(2018, 6, 25)
    assert sistema_atualizado.orgao_gestor.perfil == 0
    assert sistema_atualizado.orgao_gestor.tipo == 1


def test_cadastrar_componente_tipo_fundo_cultura(client, login, cnpj):

    sistema_cultura = mommy.make("SistemaCultura", _fill_optional=['ente_federado', 'sede', 'gestor'],
        cadastrador=login, ente_federado__cod_ibge=123456)

    url = reverse("adesao:home")
    client.get(url)

    url = reverse("planotrabalho:cadastrar_fundo_cultura")

    arquivo = SimpleUploadedFile(
        "componente.txt", b"file_content", content_type="text/plain"
    )
    cnpj = SimpleUploadedFile(
        "cnpj.txt", b"file_content", content_type="text/plain"
    )
    response = client.post(url, data={"arquivo": arquivo,
                                      "data_publicacao": '28/06/2018',
                                      "possui_cnpj": 'True',
                                      "cnpj": '28.134.084/0001-75',
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
        cadastrador=login, ente_federado__cod_ibge=123456)
    legislacao = SimpleUploadedFile(
        "legislacao.txt", b"file_content", content_type="text/plain"
    )
    sistema_cultura.legislacao.arquivo = legislacao
    sistema_cultura.legislacao.save()

    url = reverse("adesao:home")
    client.get(url)

    url = reverse("planotrabalho:cadastrar_fundo_cultura")

    response = client.post(url, data={"possui_cnpj": 'False',
                                      'mesma_lei': 'True'})

    sistema_atualizado = SistemaCultura.sistema.get(
        ente_federado__nome=sistema_cultura.ente_federado.nome)

    assert response.status_code == 302
    assert sistema_atualizado.legislacao.arquivo.name.split("/")[-1] in sistema_atualizado.fundo_cultura.arquivo.name.split("/")[-1]
    assert sistema_atualizado.legislacao.data_publicacao == sistema_atualizado.fundo_cultura.data_publicacao
    assert sistema_atualizado.fundo_cultura.tipo == 2


def test_cadastrar_componente_tipo_fundo_cultura_reaproveita_lei_com_cnpj(client, login, cnpj):

    sistema_cultura = mommy.make("SistemaCultura", _fill_optional=['ente_federado', 'sede', 'gestor', 'legislacao'],
        cadastrador=login, ente_federado__cod_ibge=123456)
    legislacao = SimpleUploadedFile(
        "legislacao_teste.txt", b"file_content", content_type="text/plain"
    )
    sistema_cultura.legislacao.arquivo = legislacao
    sistema_cultura.legislacao.save()

    url = reverse("adesao:home")
    client.get(url)

    url = reverse("planotrabalho:cadastrar_fundo_cultura")

    cnpj = SimpleUploadedFile(
        "cnpj.txt", b"file_content", content_type="text/plain"
    )
    response = client.post(url, data={"possui_cnpj": 'True',
                                      "cnpj": '28.134.084/0001-75',
                                      "comprovante": cnpj,
                                      'mesma_lei': 'True'})

    sistema_atualizado = SistemaCultura.sistema.get(
        ente_federado__nome=sistema_cultura.ente_federado.nome)

    assert response.status_code == 302
    assert sistema_atualizado.legislacao.arquivo.name.split("/")[-1] in sistema_atualizado.fundo_cultura.arquivo.name.split("/")[-1]
    assert sistema_atualizado.legislacao.data_publicacao == sistema_atualizado.fundo_cultura.data_publicacao
    assert cnpj.name.split(".")[0] in sistema_atualizado.fundo_cultura.comprovante_cnpj.arquivo.name.split("/")[-1]
    assert sistema_atualizado.fundo_cultura.cnpj == '28.134.084/0001-75'
    assert sistema_atualizado.fundo_cultura.tipo == 2


def test_cadastrar_componente_tipo_conselho(client, login):

    sistema_cultura = mommy.make("SistemaCultura", _fill_optional=['ente_federado', 'sede', 'gestor'],
        cadastrador=login, ente_federado__cod_ibge=123456)

    url = reverse("adesao:home")
    client.get(url)

    url = reverse("planotrabalho:cadastrar_conselho")

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
        cadastrador=login, ente_federado__cod_ibge=123456)
    legislacao = SimpleUploadedFile(
        "legislacao.txt", b"file_content", content_type="text/plain"
    )
    sistema_cultura.legislacao.arquivo = legislacao
    sistema_cultura.legislacao.save()

    url = reverse("adesao:home")
    client.get(url)

    url = reverse("planotrabalho:cadastrar_conselho")

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
        cadastrador=login, ente_federado__cod_ibge=123456)

    url = reverse("adesao:home")
    client.get(url)

    url = reverse("planotrabalho:cadastrar_plano")

    arquivo = SimpleUploadedFile(
        "componente.txt", b"file_content", content_type="text/plain"
    )
    anexo_lei = SimpleUploadedFile(
        "plano_lei.txt", b"file_content", content_type="text/plain"
    )
    arquivo_metas = SimpleUploadedFile(
        "plano_metas.txt", b"file_content", content_type="text/plain"
    )
    response = client.post(url, data={"arquivo": arquivo,
                                      'data_publicacao': '28/06/2018',
                                      'exclusivo_cultura': True,
                                      'ultimo_ano_vigencia': 2000,
                                      'periodicidade': 1,
                                      'mesma_lei': False,
                                      'possui_anexo': True,
                                      'anexo_na_lei': False,
                                      'anexo_lei': anexo_lei,
                                      'possui_metas': True,
                                      'metas_na_lei': False,
                                      'arquivo_metas': arquivo_metas,
                                      'monitorado': True,
                                      'local_monitoramento': "Local",
                                      'participou_curso': True,
                                      'ano_inicio_curso': 2000,
                                      'ano_termino_curso': 2001,
                                      'esfera_federacao_curso': ['1'],
                                      'tipo_oficina': ['1'],
                                      'perfil_participante': ['1']})

    sistema_atualizado = SistemaCultura.sistema.get(
        ente_federado__nome=sistema_cultura.ente_federado.nome)

    assert response.status_code == 302
    assert arquivo.name.split(".")[0] in sistema_atualizado.plano.arquivo.name.split("/")[-1]
    assert anexo_lei.name.split(".")[0] in sistema_atualizado.plano.anexo.arquivo.name.split("/")[-1]
    assert arquivo_metas.name.split(".")[0] in sistema_atualizado.plano.metas.arquivo.name.split("/")[-1]
    assert not sistema_atualizado.plano.anexo_na_lei
    assert sistema_atualizado.plano.local_monitoramento == "Local"
    assert sistema_atualizado.plano.ano_inicio_curso == 2000
    assert sistema_atualizado.plano.ano_termino_curso == 2001
    assert sistema_atualizado.plano.esfera_federacao_curso == ['1']
    assert sistema_atualizado.plano.tipo_oficina == ['1']
    assert sistema_atualizado.plano.perfil_participante == ['1']
    assert sistema_atualizado.plano.data_publicacao == datetime.date(2018, 6, 28)
    assert sistema_atualizado.plano.tipo == 4


def test_alterar_componente(client, login):

    sistema_cultura = mommy.make("SistemaCultura", _fill_optional=['ente_federado', 'legislacao', 'sede', 'gestor'],
        cadastrador=login, ente_federado__cod_ibge=123456)

    url = reverse("adesao:home")
    client.get(url)

    url = reverse("planotrabalho:alterar_legislacao", kwargs={"pk": sistema_cultura.legislacao.id})

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


def test_alterar_fundo_cultura(client, login, cnpj):

    sistema_cultura = mommy.make("SistemaCultura", _fill_optional=['ente_federado', 'fundo_cultura', 'sede', 'gestor'],
        cadastrador=login, ente_federado__cod_ibge=123456)

    url = reverse("adesao:home")
    client.get(url)

    url = reverse("planotrabalho:alterar_fundo_cultura", kwargs={"pk": sistema_cultura.fundo_cultura.id})

    numero_componentes = Componente.objects.count()
    numero_fundo_cultura = FundoDeCultura.objects.count()

    arquivo = SimpleUploadedFile(
        "novo.txt", b"file_content", content_type="text/plain"
    )
    response = client.post(url, data={"mesma_lei": "False",
                                      "possui_cnpj": "Sim",
                                      "arquivo": arquivo,
                                      "data_publicacao": "25/06/2018",
                                      "cnpj": "28.134.084/0001-75"})

    sistema_atualizado = SistemaCultura.sistema.get(
        ente_federado__nome=sistema_cultura.ente_federado.nome)

    numero_componentes_apos_update = Componente.objects.count()
    numero_fundo_cultura_apos_update = FundoDeCultura.objects.count()

    assert numero_fundo_cultura == numero_fundo_cultura_apos_update
    assert numero_componentes == numero_componentes_apos_update
    assert response.status_code == 302
    assert arquivo.name.split(".")[0] in sistema_atualizado.fundo_cultura.arquivo.name.split("/")[-1]
    assert sistema_atualizado.fundo_cultura.data_publicacao == datetime.date(2018, 6, 25)
    assert sistema_atualizado.fundo_cultura.cnpj == "28.134.084/0001-75"
    assert sistema_atualizado.fundo_cultura.tipo == 2


def test_alterar_fundo_cultura_remove_cnpj(client, login, cnpj):
    arquivo = SimpleUploadedFile(
        "novo.txt", b"file_content", content_type="text/plain"
    )
    comprovante = SimpleUploadedFile(
        "comprovante.txt", b"file_content", content_type="text/plain"
    )

    sistema_cultura = mommy.make("SistemaCultura", _fill_optional=['ente_federado', 'fundo_cultura', 'sede', 'gestor'],
        cadastrador=login, ente_federado__cod_ibge=123456)
    sistema_cultura.fundo_cultura.cnpj = "56.385.239/0001-81"
    sistema_cultura.fundo_cultura.comprovante_cnpj = mommy.make("ArquivoComponente2")
    sistema_cultura.fundo_cultura.save()

    url = reverse("adesao:home")
    client.get(url)

    url = reverse("planotrabalho:alterar_fundo_cultura", kwargs={"pk": sistema_cultura.fundo_cultura.id})

    numero_componentes = Componente.objects.count()
    numero_fundo_cultura = FundoDeCultura.objects.count()

    response = client.post(url, data={"mesma_lei": "False",
                                      "possui_cnpj": "False",
                                      "arquivo": arquivo,
                                      "data_publicacao": "25/06/2018",
                                      "cnpj": "28.134.084/0001-75",
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
        cadastrador=login, conselho=componente, ente_federado__cod_ibge=123456)

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
        cadastrador=login, ente_federado__cod_ibge=123456)

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
        cadastrador=login, ente_federado__cod_ibge=123456)
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
        cadastrador=login, ente_federado__cod_ibge=123456)
    conselheiro = mommy.make("Conselheiro", conselho=sistema.conselho)

    url = reverse("adesao:home")
    client.get(url)

    url = reverse("planotrabalho:remover_conselheiro", kwargs={'pk': conselheiro.id})
    
    response = client.post(url)

    conselheiro.refresh_from_db()

    assert conselheiro.situacao == '0'
