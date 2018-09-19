from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from planotrabalho.models import PlanoTrabalho
from planotrabalho.models import Componente


LISTA_ESTADOS_PROCESSO = (
    ('0', 'Aguardando preenchimento dos dados cadastrais'),
    ('1', 'Aguardando envio da documentação'),
    ('2', 'Documentação Recebida - Aguarda Análise'),
    ('3', 'Diligência Documental'),
    ('4', 'Encaminhado para assinatura do Secretário SAI'),
    ('5', 'Aguarda Publicação no DOU'),
    ('6', 'Publicado no DOU'),
    ('7', 'Responsável confirmado'),)

LISTA_TIPOS_FUNCIONARIOS = (
    (0, 'Secretário'),
    (1, 'Responsável'),
    (2, 'Gestor'),)


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
    mandatario = models.CharField(_("Nome do Mandataio"), max_length=300, null=True, blank=True)
    territorio = models.DecimalField(_("Área territorial - km²"), max_digits=10, decimal_places=3)
    populacao = models.IntegerField(_("População Estimada - pessoas"))
    densidade = models.DecimalField(_("Densidade demográfica - hab/km²"), max_digits=10, decimal_places=2)
    idh = models.DecimalField(_("IDH / IDHM"), max_digits=10, decimal_places=3)
    receita = models.IntegerField(_("Receitas realizadas - R$ (×1000)"), null=True, blank=True)
    despesas = models.IntegerField(_("Despesas empenhadas - R$ (×1000)"), null=True, blank=True)
    pib = models.DecimalField(_("PIB per capita - R$"), max_digits=10, decimal_places=2)


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
    complemento = models.CharField(max_length=255)
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
    link_publicacao_acordo = models.CharField(max_length=100, blank=True, null=True)
    processo_sei = models.CharField(max_length=100, blank=True, null=True)
    codigo_ativacao = models.CharField(max_length=12, unique=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)
    prazo = models.IntegerField(default=2)

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
                        "responsavel", "data_publicacao_acordo",
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
    endereco = models.CharField(max_length=255)
    complemento = models.CharField(max_length=255)
    cep = models.CharField(max_length=10)
    bairro = models.CharField(max_length=50)
    telefone_um = models.CharField(max_length=100)
    telefone_dois = models.CharField(max_length=25, blank=True)
    telefone_tres = models.CharField(max_length=25, blank=True)
    endereco_eletronico = models.URLField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.cnpj


class SistemaCulturaManager(models.Manager):
    def ativo(self, uf, cidade=None):
        """ Retorna último SistemaCultura ativo relativo a um ente federado """
        return self.filter(uf=uf, cidade=cidade).latest('data_criacao')

    def ativo_ou_cria(self, uf, cidade=None):
        """ Retorna último SistemaCultura ativo relativo a um ente federado
        caso ele não exista cria um novo SistemaCultura """
        try:
            sistema = self.ativo(uf=uf, cidade=cidade)
        except SistemaCultura.DoesNotExist:
            sistema = SistemaCultura.objects.create(uf=uf, cidade=cidade)
        return sistema

    def por_municipio(self, uf, cidade=None):
        """ Retorna todos os SistemaCultura de uma cidade ou estado """
        sistemas = self.filter(uf=uf, cidade=cidade).select_related('cadastrador', 'cidade', 'uf')

        return sistemas


class Funcionario(models.Model):
    cpf = models.CharField(
        max_length=14,
        verbose_name='CPF')
    rg = models.CharField(max_length=25, verbose_name='RG')
    orgao_expeditor_rg = models.CharField(max_length=50)
    estado_expeditor = models.ForeignKey('Uf', on_delete=models.CASCADE)
    nome = models.CharField(max_length=100)
    cargo = models.CharField(max_length=100)
    instituicao = models.CharField(max_length=100)
    telefone_um = models.CharField(max_length=25)
    telefone_dois = models.CharField(max_length=25, blank=True)
    telefone_tres = models.CharField(max_length=25, blank=True)
    email_institucional = models.EmailField()
    tipo_funcionario = models.IntegerField(
        choices=LISTA_TIPOS_FUNCIONARIOS,
        default='0')

    def __str__(self):
        return self.cpf


class Gestor(Funcionario):
    termo_posse = models.FileField(
        upload_to='termo_posse',
        max_length=255,
        blank=True,
        null=True)


class SistemaCultura(models.Model):
    """
    Entidade que representa um Sistema de Cultura
    """

    cadastrador = models.ForeignKey("Usuario", on_delete=models.SET_NULL, null=True)
    cidade = models.ForeignKey("Cidade", on_delete=models.SET_NULL, null=True)
    uf = models.ForeignKey("Uf", on_delete=models.SET_NULL, null=True)
    data_criacao = models.DateTimeField(default=timezone.now)
    legislacao = models.ForeignKey(Componente, on_delete=models.SET_NULL, null=True, related_name="legislacao")
    orgao_gestor = models.ForeignKey(Componente, on_delete=models.SET_NULL, null=True, related_name="orgao_gestor")
    fundo_cultura = models.ForeignKey(Componente, on_delete=models.SET_NULL, null=True, related_name="fundo_cultura")
    conselho = models.ForeignKey(Componente, on_delete=models.SET_NULL, null=True, related_name="conselho")
    plano = models.ForeignKey(Componente, on_delete=models.SET_NULL, null=True, related_name="plano")
    secretario = models.ForeignKey(Funcionario, on_delete=models.SET_NULL, null=True, related_name="sistema_cultura_secretario")
    responsavel = models.ForeignKey(Funcionario, on_delete=models.SET_NULL, null=True, related_name="sistema_cultura_responsavel")
    gestor = models.ForeignKey(Gestor, on_delete=models.SET_NULL, null=True)
    sede = models.ForeignKey(Sede, on_delete=models.SET_NULL, null=True)

    objects = SistemaCulturaManager()

    def compara_valores(self, obj_anterior, propriedade):
        """
        Compara os valores de determinada propriedade entre dois objetos.
        """

        return getattr(obj_anterior, propriedade) == getattr(self, propriedade)

    def save(self, *args, **kwargs):
        """
        Salva uma nova instancia de SistemaCultura sempre que alguma informação
        é alterada.
        """

        if self.pk:
            fields = self._meta.fields[1:]
            anterior = SistemaCultura.objects.get(pk=self.pk)

            comparacao = (self.compara_valores(anterior, field.attname) for field in
                          fields)

            if False in comparacao:
                self.pk = None

            if not self.compara_valores(anterior, "cadastrador"):
                self.alterar_cadastrador(anterior.cadastrador)

        super().save(*args, **kwargs)

    def alterar_cadastrador(self, cadastrador_atual):
        """
        Altera cadastrador de um ente federado fazendo as alterações
        necessárias nas models associadas ao cadastrador, gerando uma nova
        versão do sistema cultura
        """
        cadastrador = self.cadastrador
        if cadastrador_atual:
            cadastrador.recebe_permissoes_sistema_cultura(cadastrador_atual)
        else:
            try:
                ente_federado = Municipio.objects.get(estado=self.uf,
                                                      cidade=self.cidade)
                cadastrador_atual = getattr(ente_federado, 'usuario', None)
                if cadastrador_atual:
                    cadastrador.recebe_permissoes_sistema_cultura(cadastrador_atual)
                else:
                    cadastrador.municipio = ente_federado
                    cadastrador.save()
            except Municipio.DoesNotExist:
                return