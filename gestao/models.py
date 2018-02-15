from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

CLASSIFICACAO_ARQUIVO = (
    ("arquivo_danificado", "Arquivo Danificado"),
    ("arquivo_incorreto", "Arquivo incorreto"),
    ("arquivo_incompleto", "Arquivo incompleto"),
)

class Diligencia(models.Model):
    texto_diligencia = models.TextField(max_length=200)
    classificacao_arquivo = models.CharField(
        max_length=25,
        choices=CLASSIFICACAO_ARQUIVO)
    ente_federado = models.CharField(max_length=50)
    componente_type = models.ForeignKey(ContentType)
    componente_id = models.PositiveIntegerField()
    componente = GenericForeignKey('componente_type', 'componente_id')