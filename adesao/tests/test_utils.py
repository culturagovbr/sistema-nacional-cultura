import pytest

from adesao.utils import verificar_anexo
from planotrabalho.models import LISTA_SITUACAO_ARQUIVO

from django.core.files.uploadedfile import SimpleUploadedFile

from model_mommy import mommy

def test_verificar_anexo_aprovado_com_ressalvas(sistema_cultura):
    arquivo = SimpleUploadedFile(
        "componente.txt", b"file_content", content_type="text/plain"
    )
    sistema_cultura.conselho.arquivo = arquivo
    sistema_cultura.conselho.situacao = 3
    sistema_cultura.conselho.save()

    assert verificar_anexo(sistema_cultura, "conselho") == LISTA_SITUACAO_ARQUIVO[2][1]

def test_verificar_anexo_outras_situacoes(sistema_cultura):
    arquivo = SimpleUploadedFile(
        "componente.txt", b"file_content", content_type="text/plain"
    )
    sistema_cultura.conselho.arquivo = arquivo
    sistema_cultura.conselho.situacao = 4
    sistema_cultura.conselho.save()

    assert verificar_anexo(sistema_cultura, "conselho") == LISTA_SITUACAO_ARQUIVO[4][1]

def test_verificar_anexo_sem_componente():
    sistema = mommy.make("SistemaCultura")

    assert verificar_anexo(sistema, "conselho") == "Não Possui"
