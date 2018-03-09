import datetime

from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from adesao.models import Municipio 
from adesao.models import Usuario

ARQUIVO_DANIFICADO = "Arquivo Danificado"
ARQUIVO_INCOMPLETO = "Arquivo Incompleto"
ARQUIVO_INCORRETO = "Arquivo Incorreto"


class Diligencia(models.Model):
    texto_diligencia = models.TextField(max_length=200)
    classificacao_arquivo = models.ForeignKey('planotrabalho.SituacoesArquivoPlano')
    data_criacao = models.DateField(default=datetime.date.today)
    ente_federado = models.ForeignKey(Municipio)
    componente_type = models.ForeignKey(ContentType)
    componente_id = models.PositiveIntegerField()
    componente = GenericForeignKey('componente_type', 'componente_id')
    usuario = models.ForeignKey(Usuario)

    def __str__(self):
        return str(self.id)