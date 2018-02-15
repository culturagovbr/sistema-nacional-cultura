from django.db import models

from django.contrib.contenttypes.fields import GenericRelation

from gestao.models import Diligencia

SITUACAO_ENVIO = (
    (0, 'Em preenchimento'),
    (1, 'Avaliando anexo'),
    (2, 'Concluída')
    )
SITUACAO_CONSELHEIRO = (
    ('1', 'Habilitado'),
    ('0', 'Desabilitado')
    )


class PlanoTrabalho(models.Model):
    criacao_sistema = models.OneToOneField(
        'CriacaoSistema',
        blank=True,
        null=True)
    orgao_gestor = models.OneToOneField(
        'OrgaoGestor',
        blank=True,
        null=True)
    conselho_cultural = models.OneToOneField(
        'ConselhoCultural',
        blank=True,
        null=True)
    fundo_cultura = models.OneToOneField(
        'FundoCultura',
        blank=True,
        null=True)
    plano_cultura = models.OneToOneField(
        'PlanoCultura',
        blank=True,
        null=True)

    def __str__(self):
        return str(self.id)


class CriacaoSistema(models.Model):
    minuta_projeto_lei = models.FileField(
        upload_to='minuta_lei',
        max_length=255,
        blank=True,
        null=True)
    lei_sistema_cultura = models.FileField(
        upload_to='leis_sistema_cultura',
        max_length=255,
        blank=True,
        null=True)
    diligencias = GenericRelation(Diligencia, content_type_field="componente_type",
                                  object_id_field="componente_id")
    situacao_lei_sistema = models.ForeignKey('SituacoesArquivoPlano')


class OrgaoGestor(models.Model):
    relatorio_atividade_secretaria = models.FileField(
        upload_to='relatorio_atividades',
        max_length=255,
        blank=True,
        null=True)
    diligencias = GenericRelation(Diligencia, content_type_field="componente_type",
                                  object_id_field="componente_id")
    situacao_relatorio_secretaria = models.ForeignKey('SituacoesArquivoPlano')


class ConselhoCultural(models.Model):
    ata_regimento_aprovado = models.FileField(
        upload_to='regimentos',
        max_length=255,
        blank=True,
        null=True)
    diligencias = GenericRelation(Diligencia, content_type_field="componente_type",
                                  object_id_field="componente_id")
    situacao_ata = models.ForeignKey('SituacoesArquivoPlano')


class FundoCultura(models.Model):
    cnpj_fundo_cultura = models.CharField(
        max_length=18,
        verbose_name='CNPJ',
        blank=True,
        null=True,
        default=None)
    lei_fundo_cultura = models.FileField(
        upload_to='lei_fundo_cultura',
        max_length=255,
        blank=True,
        null=True)
    diligencias = GenericRelation(Diligencia, content_type_field="componente_type",
                                  object_id_field="componente_id")
    situacao_lei_plano = models.ForeignKey('SituacoesArquivoPlano')


class PlanoCultura(models.Model):
    relatorio_diretrizes_aprovadas = models.FileField(
        upload_to='relatorio_diretrizes',
        max_length=255,
        blank=True,
        null=True)
    minuta_preparada = models.FileField(
        upload_to='minuta_preparada',
        max_length=255,
        blank=True,
        null=True)
    ata_reuniao_aprovacao_plano = models.FileField(
        upload_to='ata_aprovacao_plano',
        max_length=255,
        blank=True,
        null=True)
    ata_votacao_projeto_lei = models.FileField(
        upload_to='ata_votacao_lei',
        max_length=255,
        blank=True,
        null=True)
    lei_plano_cultura = models.FileField(
        upload_to='lei_plano_cultura',
        max_length=255,
        blank=True,
        null=True)
    diligencias = GenericRelation(Diligencia, content_type_field="componente_type",
                                  object_id_field="componente_id")
    situacao_lei_plano = models.ForeignKey('SituacoesArquivoPlano')


class Conselheiro(models.Model):
    nome = models.CharField(max_length=100)
    segmento = models.CharField(max_length=255)
    email = models.EmailField(unique=False)
    situacao = models.CharField(
        blank=True,
        null=True,
        max_length=1,
        choices=SITUACAO_CONSELHEIRO,
        default=1)
    data_cadastro = models.DateField(blank=True, null=True)
    data_situacao = models.DateField(blank=True, null=True)
    conselho = models.ForeignKey('ConselhoCultural')


class SituacoesArquivoPlano(models.Model):
    descricao = models.CharField(max_length=75, null=False)
