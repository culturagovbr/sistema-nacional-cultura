from django.db import models

CLASSIFICACAO_ARQUIVO = (
    ("arquivo_danificado", "Arquivo Danificado"),
    ("arquivo_incorreto", "Arquivo incorreto"),
    ("arquivo_incompleto", "Arquivo incompleto"),
)

class Diligencia(models.Model):
    texto_diligencia = models.TextField()
    classificacao_arquivo = models.CharField(
        choices=CLASSIFICACAO_ARQUIVO)
    ente_federado = models.CharField()
    componente = models.CharField()
    