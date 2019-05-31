import datetime

from django.db import models
from django.contrib.postgres.fields import JSONField
from django.utils.text import slugify
from django.utils.translation import ugettext as _
from django.contrib.contenttypes.fields import GenericRelation
from adesao.models import *

from simple_history.models import HistoricalRecords

from gestao.models import Diligencia

SITUACAO_CONSELHEIRO = (("1", "Habilitado"), ("0", "Desabilitado"))

LISTA_TIPOS_COMPONENTES = (
    (0, 'Lei Sistema'),
    (1, 'Órgão Gestor'),
    (2, 'Fundo Cultura'),
    (3, 'Conselho Cultural'),
    (4, 'Plano Cultura'),
)

LISTA_PERIODICIDADE = (
    (0, 'Anual (1 ano)'),
    (1, 'Bienal (2 anos)'),
    (2, 'Trienal (3 anos)'),
    (3, 'Quadrienal (4 anos)'),
    (4, 'Quinquenal (5 anos)'),
    (5, 'Hexanual (6 anos)'),
    (6, 'Decenal (10 anos)'),
    (7, 'Outra'),
)

LISTA_CURSOS = (
    (0, 'Oficina'),
    (1, 'Palestra'),
    (2, 'Seminário'),
    (3, 'Pós-Graduação'),
    (4, 'Especialização'),
    (5, 'Aperfeiçoamento'),
    (6, 'Extensão'),
)

LISTA_SITUACAO_ARQUIVO = (
    (0, "Em preenchimento"),
    (1, "Avaliando anexo"),
    (2, "Concluída"),
    (3, "Arquivo aprovado com ressalvas"),
    (4, "Arquivo danificado"),
    (5, "Arquivo incompleto"),
    (6, "Arquivo incorreto"),
)

LISTA_PERFIS_ORGAO_GESTOR = (
    (0, "Não possui estrutura"),
    (1, "Órgão da administração indireta"),
    (2, "Secretaria em conjunto com outras políticas"),
    (3, "Secretaria exclusiva de cultura"),
    (4, "Setor subordinado à chefia do Executivo"),
    (5, "Setor subordinado à outra secretaria"),
    
)


def upload_to_componente(instance, filename):
    name = ''
    ext = slugify(filename.split('.').pop(-1))
    new_name = slugify(filename.rsplit('.', 1)[0])
    componente = instance._meta.object_name.lower()
    try:
        entefederado = instance.planotrabalho.usuario.municipio.id
        name = "{entefederado}/docs/{componente}/{new_name}.{ext}".format(
            entefederado=entefederado,
            componente=componente,
            new_name=new_name,
            ext=ext)
    except Exception:
        plano_id = instance.planotrabalho.id
        name = "sem_ente_federado/{plano_id}/docs/{componente}/{new_name}.{ext}".format(
                plano_id=plano_id,
                componente=componente,
                new_name=new_name,
                ext=ext)

    return name


def upload_to(instance, filename):
    componentes = {
            0: "legislacao",
            1: "orgao_gestor",
            2: "fundo_cultura",
            3: "conselho",
            4: "plano",
            }

    name = ""
    ext = slugify(filename.split(".").pop(-1))
    new_name = slugify(filename.rsplit(".", 1)[0])

    conselho = instance.conselhos.all().first()
    comprovante_cnpj = instance.comprovantes.all().first()

    if conselho:
        nome_componente = componentes.get(conselho.tipo)
    elif comprovante_cnpj:
        nome_componente = componentes.get(comprovante_cnpj.tipo)
    else:
        nome_componente = componentes.get(instance.tipo)

    name = f"docs/{nome_componente}/{instance.id}/{new_name}.{ext}"

    return name


class ArquivoComponente(models.Model):
    arquivo = models.FileField(upload_to=upload_to_componente, null=True, blank=True)
    situacao = models.ForeignKey('SituacoesArquivoPlano',
                                 on_delete=models.CASCADE,
                                 related_name='%(class)s_situacao',
                                 default=0)
    data_envio = models.DateField(default=datetime.date.today)

    class Meta:
        abstract = True


class ArquivoComponente2(models.Model):
    arquivo = models.FileField(upload_to=upload_to, null=True, blank=True)
    situacao = models.IntegerField(
        "Situação do Arquivo",
        choices=LISTA_SITUACAO_ARQUIVO,
        default=0,
    )
    diligencia = models.ForeignKey(
        'gestao.DiligenciaSimples',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='componente'
    )
    data_envio = models.DateField(default=datetime.date.today)
    data_publicacao = models.DateField(
        _("Data de Publicação do Arquivo do Componente"), null=True, blank=True)
    history = HistoricalRecords(inherit=True)


class Componente(ArquivoComponente2):
    tipo = models.IntegerField(
        choices=LISTA_TIPOS_COMPONENTES,
        default=0)

    def __str__(self):
        return str(self.id)

    def get_absolute_url(self):
        url = reverse_lazy("gestao:detalhar", kwargs={"pk": self.sistema_cultura.pk})
        return url

    @property
    def nome_componente(self):
        return LISTA_TIPOS_COMPONENTES[self.tipo][1]


class OrgaoGestor2(Componente):
    perfil = models.IntegerField(
        choices=LISTA_PERFIS_ORGAO_GESTOR, null=True, blank=True)


class FundoDeCultura(Componente):
    cnpj = models.CharField(
        max_length=18,
        verbose_name='CNPJ',
        blank=True,
        null=True,
        default=None)
    comprovante_cnpj = models.ForeignKey(
        'ArquivoComponente2',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='comprovantes')


class ConselhoDeCultura(Componente):
    lei = models.ForeignKey(
        'ArquivoComponente2',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='conselhos')
    exclusivo_cultura = models.BooleanField(blank=True, default=False)
    paritario = models.BooleanField(blank=True, default=False)


class PlanoDeCultura(Componente):
    metas = models.ForeignKey(
        'ArquivoComponente2',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='metas_plano')
    anexo = models.ForeignKey(
        'ArquivoComponente2',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='anexo_plano')
    exclusivo_cultura = models.BooleanField(blank=True, default=False)
    ultimo_ano_vigencia = models.IntegerField(blank=True)
    decenal = models.BooleanField(blank=True, default=False)
    periodicidade = models.CharField(blank=True, null=True, max_length=100)
    local_monitoramento = models.CharField(
        max_length=100,
        verbose_name='Local de Monitoramente',
        blank=True,
        null=True)
    ano_curso = models.IntegerField(blank=True, null=True)
    tipo_curso = models.IntegerField(
        "Tipo do Curso",
        choices=LISTA_CURSOS,
        blank=True,
        null=True
    )
    esfera_federacao_curso = JSONField()
    tipo_oficina = JSONField()
    perfil_participante = JSONField()



class PlanoTrabalho(models.Model):
    criacao_sistema = models.OneToOneField(
        "CriacaoSistema", on_delete=models.CASCADE, blank=True, null=True
    )
    orgao_gestor = models.OneToOneField(
        'OrgaoGestor',
        on_delete=models.CASCADE,
        blank=True,
        null=True)
    conselho_cultural = models.OneToOneField(
        'ConselhoCultural',
        on_delete=models.CASCADE,
        blank=True,
        null=True)
    fundo_cultura = models.OneToOneField(
        'FundoCultura',
        on_delete=models.CASCADE,
        blank=True,
        null=True)
    plano_cultura = models.OneToOneField(
        'PlanoCultura',
        on_delete=models.CASCADE,
        blank=True,
        null=True)
    diligencias = GenericRelation(Diligencia, content_type_field="componente_type",
                                  object_id_field="componente_id")

    def __str__(self):
        return str(self.id)


class CriacaoSistema(ArquivoComponente):
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
    data_publicacao = models.DateField(
        blank=True,
        null=True)
    diligencias = GenericRelation(Diligencia, content_type_field="componente_type",
                                  object_id_field="componente_id")


class OrgaoGestor(ArquivoComponente):
    relatorio_atividade_secretaria = models.FileField(
        upload_to='relatorio_atividades',
        max_length=255,
        blank=True,
        null=True)
    data_publicacao = models.DateField(
        blank=True,
        null=True)
    diligencias = GenericRelation(Diligencia, content_type_field="componente_type",
                                  object_id_field="componente_id")


class ConselhoCultural(ArquivoComponente):
    ata_regimento_aprovado = models.FileField(
        upload_to='regimentos',
        max_length=255,
        blank=True,
        null=True)
    data_publicacao = models.DateField(
        blank=True,
        null=True)
    diligencias = GenericRelation(Diligencia, content_type_field="componente_type",
                                  object_id_field="componente_id")


class FundoCultura(ArquivoComponente):
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
    data_publicacao = models.DateField(
        blank=True,
        null=True)
    diligencias = GenericRelation(Diligencia, content_type_field="componente_type",
                                  object_id_field="componente_id")


class PlanoCultura(ArquivoComponente):
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
    data_publicacao = models.DateField(
        blank=True,
        null=True)
    diligencias = GenericRelation(Diligencia, content_type_field="componente_type",
                                  object_id_field="componente_id")


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
    conselho = models.ForeignKey('ConselhoDeCultura', on_delete=models.CASCADE)


class SituacoesArquivoPlano(models.Model):
    descricao = models.CharField(max_length=75, null=False)

    def __str__(self):
        return self.descricao
