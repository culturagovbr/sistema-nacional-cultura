import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from model_mommy import mommy
from model_mommy.recipe import Recipe, foreign_key

from adesao.models import SistemaCultura
from planotrabalho.models import Componente


def test_criacao_novo_componente(client):
    """
    Verifica se é possível criar um novo componente.
    """
    arquivo = SimpleUploadedFile(
        "componente.txt", b"file_content", content_type="text/plain"
    )

    uf = mommy.make("Uf")
    componente = mommy.make("Componente", tipo=0)
    sistema = mommy.make("SistemaCultura", uf=uf, legislacao=componente)

    componente.arquivo = arquivo
    componente.save()
  
    assert Componente.objects.get(pk=componente.pk) == componente

    Componente.objects.all().delete()
    SistemaCultura.objects.all().delete()
