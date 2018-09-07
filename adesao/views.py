import csv
import xlwt
import xlsxwriter
import environ

from io import BytesIO
from datetime import timedelta
from threading import Thread

from django.shortcuts import render, redirect
from django.http import Http404, HttpResponse
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic import ListView, DetailView, TemplateView
from django.urls import reverse_lazy, reverse
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.template.loader import render_to_string
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db.models import Q, Count
from django.conf import settings

from templated_email.generic_views import TemplatedEmailFormViewMixin

from adesao.models import Municipio, Responsavel, Secretario, Usuario, Historico, Uf, Cidade
from planotrabalho.models import Conselheiro, PlanoTrabalho
from adesao.forms import CadastrarUsuarioForm, CadastrarMunicipioForm
from adesao.forms import CadastrarResponsavelForm, CadastrarSecretarioForm
from adesao.utils import enviar_email_conclusao, verificar_anexo

from django_weasyprint import WeasyTemplateView


# Create your views here.
def index(request):
    if request.user.is_authenticated:
        return redirect('adesao:home')
    return render(request, 'index.html')


def fale_conosco(request):
    return render(request, 'fale_conosco.html')


@login_required
def home(request):
    ente_federado = request.user.usuario.municipio
    secretario = request.user.usuario.secretario
    responsavel = request.user.usuario.responsavel
    situacao = request.user.usuario.estado_processo
    historico = Historico.objects.filter(usuario=request.user.usuario)
    historico = historico.order_by('-data_alteracao')

    if request.user.is_staff:
        return redirect('gestao:acompanhar_adesao')

    if ente_federado and secretario and responsavel and int(situacao) < 1:
        request.user.usuario.estado_processo = '1'
        request.user.usuario.save()
        message_txt = render_to_string('conclusao_cadastro.txt',
                                       {'request': request})
        message_html = render_to_string('conclusao_cadastro.email',
                                        {'request': request})
        enviar_email_conclusao(request.user, message_txt, message_html)
    return render(request, 'home.html', {'historico': historico})


def ativar_usuario(request, codigo):
    usuario = Usuario.objects.get(codigo_ativacao=codigo)

    if usuario is None:
        raise Http404()

    if timezone.now() > (usuario.data_cadastro + timedelta(days=3)):
        raise Http404()

    usuario.user.is_active = True
    usuario.save()
    usuario.user.save()

    return render(request, 'confirmar_email.html')


def sucesso_usuario(request):
    return render(request, 'usuario/mensagem_sucesso.html')


def sucesso_responsavel(request):
    return render(request, 'responsavel/mensagem_sucesso.html')


def exportar_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="dados-municipios-cadastrados-snc.csv"'
    response.write('\uFEFF')

    writer = csv.writer(response)
    writer.writerow(['UF', 'Município', 'Cod.IBGE', 'Situação', 'Endereço', 'Bairro', 'CEP', 'Telefone', 'Email'])

    for municipio in Municipio.objects.all():
        uf = municipio.estado.sigla
        if municipio.cidade:
            cidade = municipio.cidade.nome_municipio
            cod_ibge = municipio.cidade.codigo_ibge
        else:
            cidade = municipio.estado.nome_uf
            cod_ibge = ''
        try:
            estado_processo = municipio.usuario.get_estado_processo_display()
            if estado_processo != 'Publicado no DOU':
                continue
        except ObjectDoesNotExist:
            estado_processo = 'Publicado no DOU'
        endereco = municipio.endereco
        bairro = municipio.bairro
        cep = municipio.cep
        telefone = municipio.telefone_um
        email = municipio.email_institucional_prefeito
        writer.writerow([uf, cidade, cod_ibge, estado_processo, endereco, bairro, cep, telefone, email])

    return response


def exportar_ods(request):
    response = HttpResponse(content_type='application/vnd.oasis.opendocument.spreadsheet .ods')
    response['Content-Disposition'] = 'attachment; filename="dados-municipios-cadastrados-snc.ods"'

    workbook = xlwt.Workbook()
    planilha = workbook.add_sheet('SNC')
    planilha.write(0, 0, 'UF')
    planilha.write(0, 1, 'Ente Federado')
    planilha.write(0, 2, 'Cod.IBGE')
    planilha.write(0, 3, 'Situação')
    planilha.write(0, 4, 'Endereço')
    planilha.write(0, 5, 'Bairro')
    planilha.write(0, 6, 'CEP')
    planilha.write(0, 7, 'Telefone')
    planilha.write(0, 8, 'Email Prefeito')
    planilha.write(0, 9, 'Email do Cadastrador')
    planilha.write(0, 10, 'Email do Responsável')
    planilha.write(0, 11, 'Localização do processo')
    planilha.write(0, 12, 'Possui Lei do Sistema de Cultura')
    planilha.write(0, 13, 'Possui Órgão Gestor')
    planilha.write(0, 14, 'Possui Conselho de Política Cultural')
    planilha.write(0, 15, 'Possui Fundo de Cultura')
    planilha.write(0, 16, 'Possui Plano de Cultura')

    for i, municipio in enumerate(Municipio.objects.all().order_by('-cidade'), start=1):
        uf = municipio.estado.sigla
        if municipio.cidade:
            cidade = municipio.cidade.nome_municipio
            cod_ibge = municipio.cidade.codigo_ibge
        else:
            cidade = municipio.estado.nome_uf
            cod_ibge = municipio.estado.codigo_ibge
        try:
            estado_processo = municipio.usuario.get_estado_processo_display()
        except ObjectDoesNotExist:
            #Documentando: isso foi colocado aqui pois, os municipios migrados
            #fizeram adesão sem cadastrador e consequentemente estado do processo
            estado_processo = 'Publicado no DOU'
        endereco = municipio.endereco
        bairro = municipio.bairro
        cep = municipio.cep
        telefone = municipio.telefone_um
        if municipio.email_institucional_prefeito != "":
            email_prefeito = municipio.email_institucional_prefeito
        else:
            email_prefeito = "Não cadastrado"
        try:
            #email_cadastrador = Usuario.objects.get(municipio_id=municipio.id).user.email
            email_cadastrador = municipio.usuario.user.email
        except ObjectDoesNotExist:
            email_cadastrador = "Não cadastrado"
        try:
            if municipio.usuario.responsavel:
                email_responsavel = municipio.usuario.responsavel.email_institucional_responsavel
            else:
                email_responsavel = "Não cadastrado"
        except ObjectDoesNotExist:
            email_responsavel = "Não cadastrado"

        local = municipio.localizacao

        planilha.write(i, 0, uf)
        planilha.write(i, 1, cidade)
        planilha.write(i, 2, cod_ibge)
        planilha.write(i, 3, estado_processo)
        planilha.write(i, 4, endereco)
        planilha.write(i, 5, bairro)
        planilha.write(i, 6, cep)
        planilha.write(i, 7, telefone)
        planilha.write(i, 8, email_prefeito)
        planilha.write(i, 9, email_cadastrador)
        planilha.write(i, 10, email_responsavel)
        planilha.write(i, 11, local)
        planilha.write(i, 12, verificar_anexo(municipio, 'criacao_sistema', 'lei_sistema_cultura'))
        planilha.write(i, 13, verificar_anexo(municipio, 'orgao_gestor', 'relatorio_atividade_secretaria'))
        planilha.write(i, 14, verificar_anexo(municipio, 'conselho_cultural', 'ata_regimento_aprovado'))
        planilha.write(i, 15, verificar_anexo(municipio, 'fundo_cultura', 'lei_fundo_cultura'))
        planilha.write(i, 16, verificar_anexo(municipio, 'plano_cultura', 'lei_plano_cultura'))

    workbook.save(response)

    return response


def exportar_xls(request):

        output = BytesIO()

        #workbook = xlwt.Workbook()
        workbook = xlsxwriter.Workbook(output)
        #planilha = workbook.add_sheet('SNC')
        planilha = workbook.add_worksheet('SNC')

        planilha.write(0, 0, 'UF')
        planilha.write(0, 1, 'Ente Federado')
        planilha.write(0, 2, 'Cod.IBGE')
        planilha.write(0, 3, 'Situação')
        planilha.write(0, 4, 'Endereço')
        planilha.write(0, 5, 'Bairro')
        planilha.write(0, 6, 'CEP')
        planilha.write(0, 7, 'Telefone')
        planilha.write(0, 8, 'Email Prefeito')
        planilha.write(0, 9, 'Email do Cadastrador')
        planilha.write(0, 10, 'Email do Responsável')
        planilha.write(0, 11, 'Localização do processo')
        planilha.write(0, 12, 'Possui Lei do Sistema de Cultura')
        planilha.write(0, 13, 'Possui Órgão Gestor')
        planilha.write(0, 14, 'Possui Conselho de Política Cultural')
        planilha.write(0, 15, 'Possui Fundo de Cultura')
        planilha.write(0, 16, 'Possui Plano de Cultura')
        ultima_linha = 0
        for i, municipio in enumerate(Municipio.objects.all().order_by('-cidade'), start=1):
            uf = municipio.estado.sigla
            if municipio.cidade:
                cidade = municipio.cidade.nome_municipio
                cod_ibge = municipio.cidade.codigo_ibge
            else:
                cidade = municipio.estado.nome_uf
                cod_ibge = municipio.estado.codigo_ibge
            try:
                estado_processo = municipio.usuario.get_estado_processo_display()
            except ObjectDoesNotExist:
                #Documentando: isso foi colocado aqui pois, os municipios migrados
                #fizeram adesão sem cadastrador e consequentemente estado do processo
                estado_processo = 'Publicado no DOU'
            endereco = municipio.endereco
            bairro = municipio.bairro
            cep = municipio.cep
            telefone = municipio.telefone_um
            if municipio.email_institucional_prefeito != "":
                email_prefeito = municipio.email_institucional_prefeito
            else:
                email_prefeito = "Não cadastrado"
            try:
                #email_cadastrador = Usuario.objects.get(municipio_id=municipio.id).user.email
                email_cadastrador = municipio.usuario.user.email
            except ObjectDoesNotExist:
                email_cadastrador = "Não cadastrado"
            try:
                if municipio.usuario.responsavel:
                    email_responsavel = municipio.usuario.responsavel.email_institucional_responsavel
                else:
                    email_responsavel = "Não cadastrado"
            except ObjectDoesNotExist:
                email_responsavel = "Não cadastrado"

            local = municipio.localizacao

            planilha.write(i, 0, uf)
            planilha.write(i, 1, cidade)
            planilha.write(i, 2, cod_ibge)
            planilha.write(i, 3, estado_processo)
            planilha.write(i, 4, endereco)
            planilha.write(i, 5, bairro)
            planilha.write(i, 6, cep)
            planilha.write(i, 7, telefone)
            planilha.write(i, 8, email_prefeito)
            planilha.write(i, 9, email_cadastrador)
            planilha.write(i, 10, email_responsavel)
            planilha.write(i, 11, local)
            planilha.write(i, 12, verificar_anexo(municipio, 'criacao_sistema', 'lei_sistema_cultura'))
            planilha.write(i, 13, verificar_anexo(municipio, 'orgao_gestor', 'relatorio_atividade_secretaria'))
            planilha.write(i, 14, verificar_anexo(municipio, 'conselho_cultural', 'ata_regimento_aprovado'))
            planilha.write(i, 15, verificar_anexo(municipio, 'fundo_cultura', 'lei_fundo_cultura'))
            planilha.write(i, 16, verificar_anexo(municipio, 'plano_cultura', 'lei_plano_cultura'))
            ultima_linha = i

        #workbook.save(response)
        planilha.autofilter(0, 0, ultima_linha, 16)
        workbook.close()
        output.seek(0)

        response = HttpResponse(output.read(), content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename="dados-municipios-cadastrados-snc.xls"'

        return response


class CadastrarUsuario(CreateView):
    form_class = CadastrarUsuarioForm
    template_name = 'usuario/cadastrar_usuario.html'
    success_url = reverse_lazy('adesao:sucesso_usuario')

    def get_success_url(self):
        # TODO: Refatorar para usar django-templated-email
        Thread(target=send_mail, args=(
            'MINISTÉRIO DA CULTURA - SNC - CREDENCIAIS DE ACESSO',
            'Prezad@ ' + self.object.usuario.nome_usuario + ',\n' +
            'Recebemos o seu cadastro no Sistema Nacional de Cultura. ' +
            'Por favor confirme seu e-mail clicando no endereço abaixo:\n\n' +
            self.request.build_absolute_uri(reverse(
                'adesao:ativar_usuario',
                args=[self.object.usuario.codigo_ativacao])) + '\n\n' +
            'Atenciosamente,\n\n' +
            'Equipe SNC\nMinistério da Cultura',
            'naoresponda@cultura.gov.br',
            [self.object.email],),
            kwargs={'fail_silently': 'False', }
            ).start()
        return super(CadastrarUsuario, self).get_success_url()


@login_required
def selecionar_tipo_ente(request):
    return render(request, 'prefeitura/selecionar_tipo_ente.html')


def sucesso_municipio(request):
    return render(request, 'prefeitura/mensagem_sucesso_prefeitura.html')


class CadastrarMunicipio(TemplatedEmailFormViewMixin, CreateView):
    form_class = CadastrarMunicipioForm
    model = Municipio
    template_name = 'prefeitura/cadastrar_prefeitura.html'
    templated_email_template_name = 'adesao'
    templated_email_from_email = 'naoresponda@cultura.gov.br'
    success_url = reverse_lazy('adesao:sucesso_municipio')

    def templated_email_get_recipients(self, form):
        return [settings.RECEIVER_EMAIL]

    def get_context_data(self, **kwargs):
        context = super(CadastrarMunicipio, self).get_context_data(**kwargs)
        context['tipo_ente'] = self.kwargs['tipo_ente']
        return context

    def templated_email_get_context_data(self, **kwargs):
        context = super().templated_email_get_context_data(**kwargs)
        context['object'] = self.object
        return context

    def form_valid(self, form):
        self.request.user.usuario.municipio = form.save()
        self.request.user.usuario.save()
        return super(CadastrarMunicipio, self).form_valid(form)

    def dispatch(self, *args, **kwargs):
        municipio = self.request.user.usuario.municipio
        if municipio:
            return redirect('adesao:alterar_municipio', pk=municipio.id)

        return super(CadastrarMunicipio, self).dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(CadastrarMunicipio, self).get_form_kwargs()
        kwargs['user'] = self.request.user.usuario
        return kwargs


class AlterarMunicipio(UpdateView):
    form_class = CadastrarMunicipioForm
    model = Municipio
    template_name = 'prefeitura/cadastrar_prefeitura.html'
    success_url = reverse_lazy('adesao:sucesso_municipio')

    def dispatch(self, *args, **kwargs):
        municipio = self.request.user.usuario.municipio.pk
        if str(municipio) != self.kwargs['pk']:
            raise Http404()

        return super(AlterarMunicipio, self).dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(AlterarMunicipio, self).get_form_kwargs()
        kwargs['user'] = self.request.user.usuario
        return kwargs


class CadastrarResponsavel(CreateView):
    form_class = CadastrarResponsavelForm
    template_name = 'responsavel/cadastrar_responsavel.html'
    success_url = reverse_lazy('adesao:sucesso_responsavel')

    def form_valid(self, form):
        self.request.user.usuario.responsavel = form.save()
        self.request.user.usuario.save()
        return super(CadastrarResponsavel, self).form_valid(form)

    def dispatch(self, *args, **kwargs):
        responsavel = self.request.user.usuario.responsavel
        if responsavel:
            return redirect(
                'adesao:alterar_responsavel',
                pk=responsavel.id)

        return super(CadastrarResponsavel, self).dispatch(*args, **kwargs)


@login_required
def importar_secretario(request):
    secretario = request.user.usuario.secretario
    # TODO: Refatorar essa importação depois que a migração for realizada
    responsavel = Responsavel()
    if secretario:
        responsavel.cpf_responsavel = secretario.cpf_secretario
        responsavel.rg_responsavel = secretario.rg_secretario
        responsavel.orgao_expeditor_rg = secretario.orgao_expeditor_rg
        responsavel.estado_expeditor = secretario.estado_expeditor
        responsavel.nome_responsavel = secretario.nome_secretario
        responsavel.cargo_responsavel = secretario.cargo_secretario
        responsavel.instituicao_responsavel = secretario.instituicao_secretario
        responsavel.telefone_um = secretario.telefone_um
        responsavel.telefone_dois = secretario.telefone_dois
        responsavel.telefone_tres = secretario.telefone_tres
        responsavel.email_institucional_responsavel = secretario.email_institucional_secretario
        try:
            responsavel.full_clean()
            responsavel.save()
        except ValidationError:
            return redirect('adesao:responsavel')
        request.user.usuario.responsavel = responsavel
        request.user.usuario.save()
    return redirect('adesao:responsavel')


class AlterarResponsavel(UpdateView):
    form_class = CadastrarResponsavelForm
    model = Responsavel
    template_name = 'responsavel/cadastrar_responsavel.html'
    success_url = reverse_lazy('adesao:sucesso_responsavel')


def sucesso_secretario(request):
    return render(request, 'secretario/mensagem_sucesso_secretario.html')


class CadastrarSecretario(CreateView):
    form_class = CadastrarSecretarioForm
    template_name = 'secretario/cadastrar_secretario.html'
    success_url = reverse_lazy('adesao:sucesso_secretario')

    def form_valid(self, form):
        self.request.user.usuario.secretario = form.save()
        self.request.user.usuario.save()
        return super(CadastrarSecretario, self).form_valid(form)

    def dispatch(self, *args, **kwargs):
        secretario = self.request.user.usuario.secretario
        if secretario:
            return redirect('adesao:alterar_secretario', pk=secretario.id)

        return super(CadastrarSecretario, self).dispatch(*args, **kwargs)


class AlterarSecretario(UpdateView):
        form_class = CadastrarSecretarioForm
        model = Secretario
        template_name = 'secretario/cadastrar_secretario.html'
        success_url = reverse_lazy('adesao:sucesso_secretario')


class MinutaAcordo(WeasyTemplateView):
    pdf_filename = 'minuta_acordo.pdf'
    template_name = 'termos/minuta_acordo.html'

    def get_context_data(self, **kwargs):
        context = super(MinutaAcordo, self).get_context_data(**kwargs)
        context['request'] = self.request
        context['static'] = self.request.get_host()
        return context

class TermoSolicitacao(WeasyTemplateView):
    pdf_filename = 'solicitacao.pdf'
    template_name = 'termos/solicitacao.html'

    def get_context_data(self, **kwargs):
        context = super(TermoSolicitacao, self).get_context_data(**kwargs)
        context['request'] = self.request
        context['static'] = self.request.get_host()
        return context


class OficioAlteracao(WeasyTemplateView):
    pdf_filename = 'alterar_responsavel.pdf'
    template_name = 'termos/alterar_responsavel.html'

    def get_context_data(self, **kwargs):
        context = super(OficioAlteracao, self).get_context_data(**kwargs)
        context['request'] = self.request
        context['static'] = self.request.get_host()
        return context


class ConsultarMunicipios(ListView):
    template_name = 'consultar/consultar.html'
    paginate_by = '25'

    def get_queryset(self):
        ente_federado = self.request.GET.get('municipio', None)
        sistema = self.request.GET.get('sistema', None)
        orgao = self.request.GET.get('orgao', None)
        conselho = self.request.GET.get('conselho', None)
        fundo = self.request.GET.get('fundo', None)
        plano = self.request.GET.get('plano', None)

        usuarios = Municipio.objects.all()

        if sistema:
            usuarios = usuarios.filter(
                usuario__plano_trabalho__criacao_sistema__lei_sistema_cultura__isnull=False).exclude(
                usuario__plano_trabalho__criacao_sistema__lei_sistema_cultura=''
                )

        if orgao:
            usuarios = usuarios.filter(
                usuario__plano_trabalho__orgao_gestor__relatorio_atividade_secretaria__isnull=False).exclude(
                usuario__plano_trabalho__orgao_gestor__relatorio_atividade_secretaria=''
                )

        if conselho:
            usuarios = usuarios.filter(
                usuario__plano_trabalho__conselho_cultural__ata_regimento_aprovado__isnull=False).exclude(
                usuario__plano_trabalho__conselho_cultural__ata_regimento_aprovado=''
                )

        if fundo:
            usuarios = usuarios.filter(
                usuario__plano_trabalho__fundo_cultura__lei_fundo_cultura__isnull=False).exclude(
                usuario__plano_trabalho__fundo_cultura__lei_fundo_cultura=''
                )

        if plano:
            usuarios = usuarios.filter(
                usuario__plano_trabalho__plano_cultura__lei_plano_cultura__isnull=False).exclude(
                usuario__plano_trabalho__plano_cultura__lei_plano_cultura=''
                )

        if ente_federado:
            return usuarios.filter(cidade__nome_municipio__icontains=ente_federado)

        return usuarios.filter(usuario__estado_processo='6').order_by('cidade__nome_municipio')


class ConsultarEstados(ListView):
    template_name = 'consultar/consultar_estados.html'
    paginate_by = '27'

    def get_queryset(self):
        ente_federado = self.request.GET.get('estado', None)
        sistema = self.request.GET.get('sistema', None)
        orgao = self.request.GET.get('orgao', None)
        conselho = self.request.GET.get('conselho', None)
        fundo = self.request.GET.get('fundo', None)
        plano = self.request.GET.get('plano', None)

        usuarios = Municipio.objects.all()

        if sistema:
            usuarios = usuarios.filter(
                usuario__plano_trabalho__criacao_sistema__lei_sistema_cultura__isnull=False).exclude(
                usuario__plano_trabalho__criacao_sistema__lei_sistema_cultura=''
                )

        if orgao:
            usuarios = usuarios.filter(
                usuario__plano_trabalho__orgao_gestor__relatorio_atividade_secretaria__isnull=False).exclude(
                usuario__plano_trabalho__orgao_gestor__relatorio_atividade_secretaria=''
                )

        if conselho:
            usuarios = usuarios.filter(
                usuario__plano_trabalho__conselho_cultural__ata_regimento_aprovado__isnull=False).exclude(
                usuario__plano_trabalho__conselho_cultural__ata_regimento_aprovado=''
                )

        if fundo:
            usuarios = usuarios.filter(
                usuario__plano_trabalho__fundo_cultura__lei_fundo_cultura__isnull=False).exclude(
                usuario__plano_trabalho__fundo_cultura__lei_fundo_cultura=''
                )

        if plano:
            usuarios = usuarios.filter(
                usuario__plano_trabalho__plano_cultura__lei_plano_cultura__isnull=False).exclude(
                usuario__plano_trabalho__plano_cultura__lei_plano_cultura=''
                )

        if ente_federado:
            usuarios = usuarios.filter(
                Q(cidade__isnull=True),
                Q(estado__nome_uf__icontains=ente_federado) |
                Q(estado__sigla__iexact=ente_federado))

        return usuarios.filter(estado__isnull=False, cidade__isnull=True).order_by('estado')


class RelatorioAderidos(ListView):
    template_name = 'consultar/relatorio_aderidos.html'

    def get_queryset(self):

        # @TODO refatorar e usar relacionamentos diretamente do ORM django
        lista_uf = {}
        context = []

        # cria dict com estados, com estado_id como chave
        for uf in Uf.objects.order_by('sigla'):
            lista_uf[uf.codigo_ibge] = uf.sigla

        municipios_by_uf = Municipio.objects.values('estado_id').filter(
            usuario__estado_processo='6',
            cidade_id__isnull=False
            ).annotate(
                municipios_aderiram=Count('estado_id')
            )

        for estado in municipios_by_uf:
            estado['uf_sigla'] = lista_uf[estado['estado_id']]

            estado['total_municipios_uf'] = Cidade.objects.filter(uf_id=estado['estado_id']).count()

            estado['percent_mun_by_uf'] = round(
                ((estado['municipios_aderiram'] / estado['total_municipios_uf']) * 100), 2)

            context.append(estado)

        return context


class Detalhar(DetailView):
    model = Municipio
    template_name = 'consultar/detalhar.html'

    def get_context_data(self, **kwargs):
        context = super(Detalhar, self).get_context_data(**kwargs)
        try:
            planotrabalho = Usuario.objects.get(municipio_id=self.kwargs['pk'])
            if planotrabalho.plano_trabalho_id:
                conselhocultural = PlanoTrabalho.objects.get(id=planotrabalho.plano_trabalho_id)
                context['conselheiros'] = Conselheiro.objects.filter(
                    conselho_id=conselhocultural.conselho_cultural_id, situacao='1')  # Situação ativo
            return context
        except:
            context['conselheiros'] = None
            return context


class ConsultarPlanoTrabalhoMunicipio(ListView):
    template_name = 'consultar/consultar.html'
    paginate_by = '25'

    def get_queryset(self):
        ente_federado = self.request.GET.get('municipio', None)

        if ente_federado:
            return Usuario.objects.filter(
                municipio__cidade__nome_municipio__icontains=ente_federado,
                estado_processo='6')

        return Usuario.objects.filter(estado_processo='6').order_by('municipio__cidade__nome_municipio')


class ConsultarPlanoTrabalhoEstado(ListView):
    template_name = 'consultar/consultar.html'
    paginate_by = '27'

    def get_queryset(self):
        ente_federado = self.request.GET.get('estado', None)

        if ente_federado:
            return Usuario.objects.filter(
                Q(municipio__cidade__isnull=True),
                Q(municipio__estado__nome_uf__icontains=ente_federado) |
                Q(municipio__estado__sigla__iexact=ente_federado))

        return Usuario.objects.filter(municipio__estado__isnull=False, municipio__cidade__isnull=True)
