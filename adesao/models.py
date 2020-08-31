import math
import re

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse_lazy
from django.contrib.contenttypes.fields import GenericRelation

from planotrabalho.models import PlanoTrabalho
from planotrabalho.models import PlanoDeCultura
from planotrabalho.models import Componente
from planotrabalho.models import ConselhoDeCultura
from planotrabalho.models import OrgaoGestor2
from planotrabalho.models import LISTA_SITUACAO_ARQUIVO

from gestao.models import Diligencia

from planotrabalho.models import FundoDeCultura

from adesao.managers import SistemaManager
from adesao.managers import HistoricoManager

from datetime import date
from adesao.middleware import get_current_user

from itertools import tee

from django.db import connection

LISTA_ESTADOS_PROCESSO = (
    ('0', 'Aguardando preenchimento dos dados cadastrais'),
    ('1', 'Aguardando envio da documentação'),
    ('2', 'Aguardando renovação da adesão'),
    ('3', 'Diligência Documental'),
    ('4', 'Aguardando análise do Plano de Trabalho'),
    ('5', 'Diligência Documental'),
    ('6', 'Publicado no DOU'),
    ('7', 'Acordo de Cooperação e Termo de Adesão aprovados'),
    )

LISTA_TIPOS_FUNCIONARIOS = (
    (0, 'Gestor de Cultura'),
    (1, 'Responsável'),
    (2, 'Gestor'),)

UFS = {
    12: "AC",
    27: "AL",
    13: "AM",
    16: "AP",
    29: "BA",
    23: "CE",
    53: "DF",
    32: "ES",
    52: "GO",
    21: "MA",
    31: "MG",
    50: "MS",
    51: "MT",
    15: "PA",
    25: "PB",
    26: "PE",
    22: "PI",
    41: "PR",
    33: "RJ",
    24: "RN",
    11: "RO",
    14: "RR",
    43: "RS",
    42: "SC",
    28: "SE",
    35: "SP",
    17: "TO"
}

REGIOES = {
    '1': "Norte",
    '2': "Nordeste",
    '3': "Sudeste",
    '4': "Sul",
    '5': "Centro Oeste",
}


# Create your models here.
class Uf(models.Model):
    codigo_ibge = models.IntegerField(primary_key=True)
    sigla = models.CharField(max_length=2)
    nome_uf = models.CharField(max_length=100)

    def __str__(self):
        return self.sigla

    class Meta:
        ordering = ['sigla']


class EnteFederado(models.Model):
    cod_ibge = models.IntegerField(_('Código IBGE'))
    nome = models.CharField(_("Nome do EnteFederado"), max_length=300)
    gentilico = models.CharField(_("Gentilico"), max_length=300, null=True, blank=True)
    mandatario = models.CharField(_("Nome do Mandataio"), max_length=300, null=True, blank=True)
    territorio = models.DecimalField(_("Área territorial - km²"), max_digits=15, decimal_places=3)
    populacao = models.IntegerField(_("População Estimada - pessoas"))
    densidade = models.DecimalField(_("Densidade demográfica - hab/km²"), null=True, blank=True, max_digits=10,
                                    decimal_places=2)
    idh = models.DecimalField(_("IDH / IDHM"), max_digits=10, decimal_places=3, null=True, blank=True)
    receita = models.IntegerField(_("Receitas realizadas - R$ (×1000)"), null=True, blank=True)
    despesas = models.IntegerField(_("Despesas empenhadas - R$ (×1000)"), null=True, blank=True)
    pib = models.DecimalField(_("PIB per capita - R$"), max_digits=10, decimal_places=2)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    def __str__(self):

        uf = UFS.get(self.cod_ibge, UFS.get(int(str(self.cod_ibge)[:2])))

        digits = int(math.log10(self.cod_ibge)) + 1

        if digits > 2 or self.cod_ibge == 53:
            return f"{self.nome}/{uf}"

        return f"Estado de {self.nome} ({uf})"

    def get_regiao(self):
        digito = str(self.cod_ibge)[0]
        regiao = REGIOES[digito]
        return regiao

    def faixa_populacional(self):

        if self.populacao <= 5000:
            faixa = "Até 5.000"
        elif self.populacao <= 10000:
            faixa = "De 5.001 até 10.000"
        elif self.populacao <= 20000:
            faixa = "De 10.001 até 20.000"
        elif self.populacao <= 50000:
            faixa = "De 20.001 até 50.000"
        elif self.populacao <= 100000:
            faixa = "De 50.001 até 100.000"
        elif self.populacao <= 500000:
            faixa = "De 100.001 até 500.000"
        else:
            faixa = "Acima de 500.000"
        return faixa

    @property
    def is_municipio(self):
        digits = int(math.log10(self.cod_ibge)) + 1

        if digits > 2:
            return True
        return False

    @property
    def sigla(self):
        if self.is_municipio is False and self.cod_ibge != 53:
            uf = re.search('\(([A-Z]+)\)', self.__str__())[0]
            return re.search('[A-Z]+', uf)[0]

        return re.search('(\/[A-Z]*)', self.__str__())[0][1:]

    class Meta:
        indexes = [models.Index(fields=['cod_ibge']), ]


class Cidade(models.Model):
    codigo_ibge = models.IntegerField(unique=True)
    uf = models.ForeignKey('Uf',
                           to_field='codigo_ibge',
                           on_delete=models.CASCADE)
    nome_municipio = models.CharField(max_length=100)
    lat = models.FloatField()
    lng = models.FloatField()

    def __str__(self):
        return self.nome_municipio

    class Meta:
        ordering = ['nome_municipio']


class Municipio(models.Model):
    localizacao = models.CharField(max_length=50, blank=True)
    numero_processo = models.CharField(max_length=50, blank=True)
    cpf_prefeito = models.CharField(
        max_length=14,
        verbose_name='CPF')
    nome_prefeito = models.CharField(max_length=255)
    cnpj_prefeitura = models.CharField(
        max_length=18,
        verbose_name='CNPJ')
    rg_prefeito = models.CharField(max_length=50, verbose_name='RG')
    orgao_expeditor_rg = models.CharField(max_length=50)
    estado_expeditor = models.ForeignKey('Uf',
                                         related_name='estado_expeditor',
                                         on_delete=models.CASCADE)
    endereco = models.CharField(max_length=255)
    complemento = models.CharField(max_length=255, default='', blank=True)
    cep = models.CharField(max_length=10)
    bairro = models.CharField(max_length=50)
    estado = models.ForeignKey('Uf', on_delete=models.CASCADE)
    cidade = models.ForeignKey('Cidade', on_delete=models.CASCADE,
                               null=True, blank=True)
    telefone_um = models.CharField(max_length=100)
    telefone_dois = models.CharField(max_length=25, blank=True)
    telefone_tres = models.CharField(max_length=25, blank=True)
    endereco_eletronico = models.URLField(max_length=255, blank=True, null=True)
    email_institucional_prefeito = models.EmailField()
    termo_posse_prefeito = models.FileField(
        upload_to='termo_posse',
        max_length=255,
        blank=True,
        null=True)
    rg_copia_prefeito = models.FileField(
        upload_to='rg_copia',
        max_length=255,
        blank=True,
        null=True)
    cpf_copia_prefeito = models.FileField(
        upload_to='cpf_copia',
        max_length=255,
        blank=True,
        null=True)

    def __str__(self):
        return self.cnpj_prefeitura

    class Meta:
        unique_together = ('cidade', 'estado')


class Responsavel(models.Model):
    cpf_responsavel = models.CharField(
        max_length=14,
        verbose_name='CPF')
    rg_responsavel = models.CharField(max_length=25, verbose_name='RG')
    orgao_expeditor_rg = models.CharField(max_length=50)
    estado_expeditor = models.ForeignKey('Uf', on_delete=models.CASCADE)
    nome_responsavel = models.CharField(max_length=100)
    cargo_responsavel = models.CharField(max_length=100)
    instituicao_responsavel = models.CharField(max_length=100)
    telefone_um = models.CharField(max_length=25)
    telefone_dois = models.CharField(max_length=25, blank=True)
    telefone_tres = models.CharField(max_length=25, blank=True)
    email_institucional_responsavel = models.EmailField()

    def __str__(self):
        return self.cpf_responsavel


class Secretario(models.Model):
    cpf_secretario = models.CharField(
        max_length=14,
        verbose_name='CPF')
    rg_secretario = models.CharField(max_length=25, verbose_name='RG')
    orgao_expeditor_rg = models.CharField(max_length=50)
    estado_expeditor = models.ForeignKey('Uf', on_delete=models.CASCADE)
    nome_secretario = models.CharField(max_length=100)
    cargo_secretario = models.CharField(max_length=100)
    instituicao_secretario = models.CharField(max_length=100)
    telefone_um = models.CharField(max_length=25)
    telefone_dois = models.CharField(max_length=25, blank=True)
    telefone_tres = models.CharField(max_length=25, blank=True)
    email_institucional_secretario = models.EmailField()

    def __str__(self):
        return self.cpf_secretario


class Usuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nome_usuario = models.CharField(max_length=100)
    municipio = models.OneToOneField('Municipio', on_delete=models.CASCADE,
                                     blank=True, null=True)
    responsavel = models.OneToOneField('Responsavel', on_delete=models.CASCADE,
                                       blank=True, null=True)
    secretario = models.OneToOneField('Secretario', on_delete=models.CASCADE,
                                      blank=True, null=True)
    plano_trabalho = models.OneToOneField(
        'planotrabalho.PlanoTrabalho',
        on_delete=models.CASCADE,
        blank=True,
        null=True)
    estado_processo = models.CharField(
        max_length=1,
        choices=LISTA_ESTADOS_PROCESSO,
        default='0')
    data_publicacao_acordo = models.DateField(blank=True, null=True)
    link_publicacao_acordo = models.CharField(max_length=200, blank=True, null=True)
    processo_sei = models.CharField(max_length=100, blank=True, null=True)
    codigo_ativacao = models.CharField(max_length=12, unique=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)
    prazo = models.IntegerField(default=2)
    email_pessoal = models.EmailField(blank=True, null=True)

    def __str__(self):
        return self.user.username

    def limpa_cadastrador(self):
        """
        Remove referência do cadastrador alterado para as tabelas PlanoTrabalho,
        Secretario, Reponsavel e Municipio
        """
        self.plano_trabalho = None
        self.municipio = None
        self.responsavel = None
        self.secretario = None
        self.user.save()

        self.save()

    def transfere_propriedade(self, propriedade, valor):
        """
        Transfere um determinado valor para uma propriedade da instancia de
        Usuario
        """
        setattr(self, propriedade, valor)

    def recebe_permissoes_sistema_cultura(self, usuario):
        """
        Recebe de um outro usuário o seu PlanoTrabalho, Municipio, Secretario,
        Responsavel, DataPublicacaoAcordo e EstadoProcesso.
        """

        propriedades = ("plano_trabalho", "municipio", "secretario",
                        "responsavel", "data_publicacao_acordo", "data_publicacao_retificacao",
                        "estado_processo")

        for propriedade in propriedades:
            valor = getattr(usuario, propriedade, None)
            self.transfere_propriedade(propriedade, valor)

        usuario.limpa_cadastrador()
        self.save()

    def save(self, *args, **kwargs):
        if self.pk:
            if self.estado_processo == '6' and self.plano_trabalho is None:
                self.plano_trabalho = PlanoTrabalho.objects.create()

        super(Usuario, self).save(*args, **kwargs)


class Historico(models.Model):
    usuario = models.ForeignKey('Usuario', on_delete=models.CASCADE)
    situacao = models.CharField(
        max_length=1,
        choices=LISTA_ESTADOS_PROCESSO,
        blank=True,
        null=True)
    data_alteracao = models.DateTimeField(auto_now_add=True)
    arquivo = models.FileField(upload_to='historico', blank=True, null=True)
    descricao = models.TextField(blank=True, null=True)


class Sede(models.Model):
    localizacao = models.CharField(max_length=50, blank=True)
    cnpj = models.CharField(
        max_length=18,
        verbose_name='CNPJ')
    endereco = models.TextField()
    complemento = models.CharField(max_length=255, default='', blank=True)
    cep = models.CharField(max_length=10)
    bairro = models.CharField(max_length=50)
    telefone_um = models.CharField(max_length=100)
    telefone_dois = models.CharField(max_length=25, blank=True)
    telefone_tres = models.CharField(max_length=25, blank=True)
    endereco_eletronico = models.URLField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.cnpj


class Funcionario(models.Model):
    cpf = models.CharField(
        max_length=14,
        verbose_name='CPF')
    rg = models.CharField(max_length=50, verbose_name='RG')
    orgao_expeditor_rg = models.CharField(max_length=50)
    estado_expeditor = models.ForeignKey('Uf',
                                         on_delete=models.CASCADE,
                                         choices=UFS.items())
    nome = models.CharField(max_length=100)
    cargo = models.CharField(max_length=100, null=True, blank=True)
    instituicao = models.CharField(max_length=100, null=True, blank=True)
    telefone_um = models.CharField(max_length=50)
    telefone_dois = models.CharField(max_length=50, blank=True)
    telefone_tres = models.CharField(max_length=50, blank=True)
    email_institucional = models.EmailField()
    email_pessoal = models.EmailField(null=True, blank=True)
    tipo_funcionario = models.IntegerField(
        choices=LISTA_TIPOS_FUNCIONARIOS,
        default='0')
    estado_endereco = models.ForeignKey('Uf',
                                        related_name='funcionario_estado_endereco',
                                        on_delete=models.CASCADE,
                                        choices=UFS.items(),
                                        null=True)
    endereco = models.CharField(max_length=255, null=True)
    complemento = models.CharField(max_length=255, default='', blank=True)
    cep = models.CharField(max_length=10, null=True)
    bairro = models.CharField(max_length=50, null=True)

    def __str__(self):
        return self.cpf


class Gestor(Funcionario):
    termo_posse = models.FileField(
        upload_to='termo_posse',
        max_length=255,
        blank=True,
        null=True)
    rg_copia = models.FileField(
        upload_to='rg_copia',
        max_length=255,
        blank=True,
        null=True)
    cpf_copia = models.FileField(
        upload_to='cpf_copia',
        max_length=255,
        blank=True,
        null=True)


class SistemaCultura(models.Model):
    """
    Entidade que representa um Sistema de Cultura
    """
    oficio_cadastrador = models.FileField(
        upload_to='oficio_cadastrador',
        max_length=255,
        null=True)
    oficio_prorrogacao_prazo = models.FileField(
        upload_to='oficio_prorrogacao_prazo',
        max_length=255,
        null=True)
    cadastrador = models.ForeignKey("Usuario", on_delete=models.SET_NULL, null=True, related_name="sistema_cultura")
    ente_federado = models.ForeignKey("EnteFederado", on_delete=models.SET_NULL, null=True)
    data_criacao = models.DateTimeField(default=timezone.now)
    legislacao = models.ForeignKey(Componente, on_delete=models.SET_NULL, null=True, related_name="legislacao")
    orgao_gestor = models.ForeignKey(OrgaoGestor2, on_delete=models.SET_NULL, null=True, related_name="orgao_gestor")
    fundo_cultura = models.ForeignKey(FundoDeCultura, on_delete=models.SET_NULL, null=True,
                                      related_name="fundo_cultura")
    conselho = models.ForeignKey(ConselhoDeCultura, on_delete=models.SET_NULL, null=True, related_name="conselho")
    plano = models.ForeignKey(PlanoDeCultura, on_delete=models.SET_NULL, null=True, related_name="plano")

    gestor_cultura = models.ForeignKey(Funcionario, on_delete=models.SET_NULL, null=True,
                                       related_name="sistema_cultura_gestor_cultura")
    gestor = models.ForeignKey(Gestor, on_delete=models.SET_NULL, null=True)
    sede = models.ForeignKey(Sede, on_delete=models.SET_NULL, null=True)
    estado_processo = models.CharField(
        max_length=1,
        choices=LISTA_ESTADOS_PROCESSO,
        default='0')
    data_publicacao_acordo = models.DateField(blank=True, null=True)
    data_publicacao_retificacao = models.DateField(blank=True, null=True)
    link_publicacao_acordo = models.CharField(max_length=200, blank=True, null=True)
    link_publicacao_retificacao = models.CharField(max_length=200, blank=True, null=True)
    processo_sei = models.CharField(max_length=100, blank=True, null=True)
    numero_processo = models.CharField(max_length=50, null=True, blank=True)
    localizacao = models.CharField(_("Localização do Processo"), max_length=10, blank=True, null=True)
    justificativa = models.TextField(_("Justificativa"), blank=True, null=True)
    diligencia = models.ForeignKey("gestao.DiligenciaSimples", on_delete=models.SET_NULL,
                                   related_name="sistema_cultura", blank=True, null=True)
    prazo = models.IntegerField(default=2)
    conferencia_nacional = models.BooleanField(blank=True, default=False)
    alterado_em = models.DateTimeField("Alterado em", default=timezone.now)
    alterado_por = models.ForeignKey("Usuario", on_delete=models.SET_NULL, null=True, related_name="sistemas_alterados")

    objects = models.Manager()
    sistema = SistemaManager()
    historico = HistoricoManager()

    class Meta:
        ordering = ['ente_federado__nome', 'ente_federado', '-alterado_em']

    def get_absolute_url(self):
        url = reverse_lazy("gestao:detalhar", kwargs={"cod_ibge": self.ente_federado.cod_ibge})
        return url

    def get_componentes_diligencias(self, componente=None, arquivo='arquivo'):
        diligencias_componentes = []
        if componente:
            componentes = [componente]
        else:
            componentes = ['legislacao', 'orgao_gestor',
                           'plano', 'conselho', 'fundo_cultura']

        for componente in componentes:
            componente = getattr(self, componente)

            if arquivo != 'arquivo':
                componente = getattr(componente, arquivo)

            if componente and componente.diligencia:
                componente.historico_diligencia = componente.diligencia.history.all()
                diligencias_componentes.append(componente)
        return diligencias_componentes

    def atualiza_relacoes_reversas(self, anterior):
        for field in anterior._meta.get_fields():
            if field.auto_created and not field.concrete:
                objetos = getattr(anterior, field.name)
                for objeto in objetos.all():
                    objeto.sistema_cultura = self
                    objeto.save()

    def historico_cadastradores(self):
        sistemas = SistemaCultura.historico.ente(self.ente_federado.cod_ibge)
        sistema_base = sistemas.first()
        historico_cadastradores = [sistema_base]

        for sistema in sistemas:
            if sistema.cadastrador != sistema_base.cadastrador:
                historico_cadastradores.append(sistema)
                sistema_base = sistema

        return historico_cadastradores

    def get_situacao_componentes(self):
        """
        Retornar uma lista contendo a situação de cada componente e comporvante CNPJ de um SistemaCultura
        """
               
        componentes = ('legislacao', 'orgao_gestor', 'orgao_gestor_cnpj','fundo_cultura', 'fundo_cultura_cnpj', 'conselho', 'plano')
        objetos = (getattr(self, componente, None) for componente in componentes)

        situacoes = {componente: objeto.get_situacao_display() for (componente, objeto) in zip(componentes, objetos) if
                     objeto is not None }
        comp = {}

        if self.orgao_gestor:
            if self.orgao_gestor.comprovante_cnpj:
                comp.update({'orgao_gestor_cnpj' : LISTA_SITUACAO_ARQUIVO[self.orgao_gestor.comprovante_cnpj.situacao][1]} )

        if self.fundo_cultura:
            if self.fundo_cultura.comprovante_cnpj:
                comp.update({'fundo_cultura_cnpj' : LISTA_SITUACAO_ARQUIVO[self.fundo_cultura.comprovante_cnpj.situacao][1]} )

        if comp:
            situacoes.update(comp)

        return situacoes

    def compara_valores(self, obj_anterior, fields):
        """
        Compara os valores de determinada propriedade entre dois objetos.
        """
        return (getattr(obj_anterior, field.attname) == getattr(self, field.attname) for field in
                fields)

    def compara_fks(self, obj_anterior, fields):
        comparacao_fk = True

        for field in fields:
            if field.get_internal_type() == 'ForeignKey':

                objeto_fk_anterior = getattr(obj_anterior, field.name)
                objeto_fk_atual = getattr(self, field.name)

                if objeto_fk_anterior and objeto_fk_atual:
                    for field in field.related_model._meta.fields[1:]:
                        objeto_fk_anterior_value = getattr(objeto_fk_anterior, field.name)
                        objeto_fk_atual_value = getattr(objeto_fk_atual, field.name)

                        if objeto_fk_anterior_value != objeto_fk_atual_value:
                            comparacao_fk = False
                            break

                    if not comparacao_fk:
                        break

        return comparacao_fk

    def get_estado_processo_display(self):
        estado_index = int(self.estado_processo)
        return LISTA_ESTADOS_PROCESSO[estado_index][1]

    def save(self, *args, **kwargs):
        """
        Salva uma nova instancia de SistemaCultura sempre que alguma informação
        é alterada.
        """

        if self.pk:
            fields = self._meta.fields[1:-1]
            anterior = SistemaCultura.objects.get(pk=self.pk)

            comparacao_fk = True

            if all(self.compara_valores(anterior, fields)):
                comparacao_fk = self.compara_fks(anterior, fields)

            if False in self.compara_valores(anterior, fields) or comparacao_fk == False:
                self.pk = None
                self.alterado_em = timezone.now()
                self.alterado_por = get_current_user()

                super().save(*args, **kwargs)
                self.atualiza_relacoes_reversas(anterior)
        else:
            super().save(*args, **kwargs)

    def has_not_diligencias_enviadas_aprovadas(self):
        query = '''SELECT COUNT(ad_sc.id) <= 0
                      FROM adesao_sistemacultura ad_sc
                      JOIN planotrabalho_componente pt_cl
                        ON pt_cl.arquivocomponente2_ptr_id = ad_sc.legislacao_id
                      JOIN planotrabalho_arquivocomponente2 pt_acl
                        ON pt_acl.id = pt_cl.arquivocomponente2_ptr_id
                       AND pt_acl.situacao IN (2, 3)
                      JOIN planotrabalho_componente pt_cp
                        ON pt_cp.arquivocomponente2_ptr_id = ad_sc.plano_id
                      JOIN planotrabalho_arquivocomponente2 pt_acp
                        ON pt_acp.id = pt_cp.arquivocomponente2_ptr_id
                       AND pt_acp.situacao IN (2, 3)
                      JOIN planotrabalho_componente pt_cc
                        ON pt_cc.arquivocomponente2_ptr_id = ad_sc.conselho_id
                      JOIN planotrabalho_arquivocomponente2 pt_acc
                        ON pt_acc.id = pt_cc.arquivocomponente2_ptr_id
                       AND pt_acc.situacao IN (2, 3)
                      JOIN planotrabalho_componente pt_cf
                        ON pt_cf.arquivocomponente2_ptr_id = ad_sc.fundo_cultura_id
                      JOIN planotrabalho_arquivocomponente2 pt_acf
                        ON pt_acf.id = pt_cf.arquivocomponente2_ptr_id
                       AND pt_acf.situacao IN (2, 3)
                      JOIN planotrabalho_componente pt_co
                        ON pt_co.arquivocomponente2_ptr_id = ad_sc.orgao_gestor_id
                      JOIN planotrabalho_arquivocomponente2 pt_aco
                        ON pt_aco.id = pt_co.arquivocomponente2_ptr_id
                       AND pt_aco.situacao IN (2, 3)
                     WHERE ad_sc.ente_federado_id = %s
                       AND ad_sc.diligencia_id IS NOT NULL'''

        cursor = connection.cursor()
        cursor.execute(query, [self.ente_federado.id])

        row = cursor.fetchone()

        return row[0]


class BaseSolicitacao(models.Model):
    """
    Requerimento de Troca Cadastrado
    """
    
    class Meta:
        abstract = True

    STATUS = (
        ('0', 'Pendente de Análise'),
        ('1', 'Aprovado'),
        ('2', 'Rejeitado'),
    )
    ente_federado = models.ForeignKey("EnteFederado", on_delete=models.SET_NULL, null=True)
    alterado_por = models.ForeignKey('Usuario', on_delete=models.SET_NULL, null=True, related_name="%(class)s_alterado_por")
    status = models.CharField(max_length=1, choices=STATUS, default='0', blank=True, null=True)
    alterado_em = models.DateTimeField("Alterado em", default=timezone.now)
    oficio = models.FileField(upload_to='oficio', max_length=255, null=True)
    laudo = models.TextField(blank=True, null=True)
    avaliador = models.ForeignKey('Usuario', on_delete=models.SET_NULL, null=True, related_name="%(class)s_avaliador")
    data_analise = models.DateTimeField("Data de Análise", blank=True, null=True)
    
    def save(self, *args, **kwargs):
        """
        Salva uma nova instancia 
        """

        if self.pk:
                self.alterado_em = timezone.now()
                super().save(*args, **kwargs)
        else:
            self.alterado_em = timezone.now()
            self.alterado_por = get_current_user()
            super().save(*args, **kwargs)

    def get_estado_processo_display(self):
        estado_index = int(self.status)
        return self.STATUS[estado_index][1]

    def __str__(self):
        return "Solicitação de "+str(self.ente_federado)

class SolicitacaoDeAdesao(BaseSolicitacao):
    def __str__(self):
        return "Solicitação de Adesão de "+str(self.ente_federado)

class SolicitacaoDeTrocaDeCadastrador(BaseSolicitacao):
    def __str__(self):
        return "Solicitação de Troca de Cadastrador de "+str(self.ente_federado)