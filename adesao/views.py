import csv
import xlwt
import xlsxwriter

from io import BytesIO
from datetime import timedelta
from threading import Thread

from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, HttpResponse
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic import ListView, DetailView
from django.urls import reverse_lazy, reverse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.template.loader import render_to_string
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db.models import Q, Count
from django.conf import settings
from django.forms.models import model_to_dict

from templated_email.generic_views import TemplatedEmailFormViewMixin

from adesao.models import (
    SistemaCultura,
    Municipio,
    Responsavel,
    Secretario,
    Usuario,
    Historico,
    Uf,
    Cidade,
    Funcionario
)
from planotrabalho.models import Conselheiro, PlanoTrabalho
from adesao.forms import CadastrarUsuarioForm, CadastrarSistemaCulturaForm
from adesao.forms import CadastrarSede, CadastrarGestor
from adesao.forms import CadastrarFuncionarioForm
from adesao.utils import enviar_email_conclusao, verificar_anexo
from adesao.utils import atualiza_session, preenche_planilha

from django_weasyprint import WeasyTemplateView
from templated_email import send_templated_mail


# Create your views here.
def index(request):
    if request.user.is_authenticated:
        return redirect("adesao:home")
    return render(request, "index.html")


def fale_conosco(request):
    return render(request, "fale_conosco.html")


@login_required
def home(request):
    ente_federado = request.session.get('sistema_ente', False)
    gestor_cultura = request.session.get('sistema_gestor_cultura', False)
    sistema = request.session.get('sistema_cultura_selecionado', False)
    historico = Historico.objects.filter(usuario=request.user.usuario)
    historico = historico.order_by("-data_alteracao")
    sistemas_cultura = SistemaCultura.sistema.filter(cadastrador=request.user.usuario)

    if not sistemas_cultura:
        request.session.pop('sistema_cultura_selecionado', None)

    request.session['sistemas'] = list(sistemas_cultura.values('id', 'ente_federado__nome'))

    if request.user.is_staff:
        return redirect("gestao:acompanhar_adesao")

    if sistemas_cultura.count() == 1:
        atualiza_session(sistemas_cultura[0], request)

    if ente_federado and gestor_cultura and sistema and int(sistema['estado_processo']) < 1:
        sistema = SistemaCultura.sistema.get(id=sistema['id'])
        sistema.estado_processo = "1"
        sistema.save()

        sistema_atualizado = SistemaCultura.sistema.get(ente_federado__cod_ibge=ente_federado['cod_ibge'])
        atualiza_session(sistema_atualizado, request)

        enviar_email_conclusao(request)
    return render(request, "home.html", {"historico": historico})


def define_sistema_sessao(request):
    sistema = request.POST.get('sistema')
    sistema_cultura = SistemaCultura.sistema.get(id=sistema)

    atualiza_session(sistema_cultura, request)

    return redirect("adesao:home")


def ativar_usuario(request, codigo):
    usuario = Usuario.objects.get(codigo_ativacao=codigo)

    if usuario is None:
        raise Http404()

    if timezone.now() > (usuario.data_cadastro + timedelta(days=3)):
        raise Http404()

    usuario.user.is_active = True
    usuario.save()
    usuario.user.save()

    return render(request, "confirmar_email.html")


def sucesso_usuario(request):
    return render(request, "usuario/mensagem_sucesso.html")


def sucesso_funcionario(request, **kwargs):
    return render(request, "mensagem_sucesso.html")


def exportar_csv(request):
    response = HttpResponse(content_type="text/csv")
    response[
        "Content-Disposition"
    ] = 'attachment; filename="dados-municipios-cadastrados-snc.csv"'
    response.write("\uFEFF")

    writer = csv.writer(response)
    writer.writerow(
        [
            "Nome",
            "UF",
            "Região",
            "Cod.IBGE",
            "PIB [2016]",
            "IDH [2010]",
            "População [2018]",
            "Faixa Populacional",
            "Situação",
            "Situação da Lei do Sistema de Cultura",
            "Situação do Órgão Gestor",
            "Situação do Conselho de Política Cultural",
            "Situação do Fundo de Cultura",
            "Situação do Plano de Cultura",
            "Participou da Conferência Nacional",
            "Endereço",
            "Bairro",
            "CEP",
            "Telefone",
            "Email",
            "Última atualização",
        ]
    )

    for sistema in SistemaCultura.objects.distinct('ente_federado__cod_ibge').order_by(
        'ente_federado__cod_ibge', 'ente_federado__nome', '-alterado_em'):
        if sistema.ente_federado:
            if sistema.ente_federado.cod_ibge > 100 or sistema.ente_federado.cod_ibge == 53:
                nome = sistema.ente_federado.nome
            else:
                nome = "Estado de " + sistema.ente_federado.nome
            cod_ibge = sistema.ente_federado.cod_ibge
            sigla = sistema.ente_federado.sigla
            regiao = sistema.ente_federado.get_regiao()
            pib = sistema.ente_federado.pib
            idh = sistema.ente_federado.idh
            populacao = sistema.ente_federado.populacao
            faixa_populacional = sistema.ente_federado.faixa_populacional()
        else:
            nome = "Nome não cadastrado"
            cod_ibge = "Código não cadastrado"
            regiao = "Não encontrada"
            sigla = "Não encontrada"
            pib = "Não encontrado"
            idh = "Não encontrado"
            populacao = "Não encontrada"
            faixa_populacional = "Não encontrada"

        estado_processo = sistema.get_estado_processo_display()

        if sistema.sede:
            endereco = sistema.sede.endereco
            bairro = sistema.sede.bairro
            cep = sistema.sede.cep
            telefone = sistema.sede.telefone_um
        else:
            endereco = "Não cadastrado"
            bairro = "Não cadastrado"
            cep = "Não cadastrado"
            telefone = "Não cadastrado"

        if sistema.gestor:
            email = sistema.gestor.email_institucional
        else:
            email = "Não cadastrado"

        writer.writerow(
            [
                nome,
                sigla,
                regiao,
                cod_ibge,
                pib,
                idh,
                populacao,
                faixa_populacional,
                estado_processo,
                verificar_anexo(sistema, "legislacao"),
                verificar_anexo(sistema, "orgao_gestor"),
                verificar_anexo(sistema, "conselho"),
                verificar_anexo(sistema, "fundo_cultura"),
                verificar_anexo(sistema, "plano"),
                "Sim" if sistema.conferencia_nacional else "Não",
                endereco,
                bairro,
                cep,
                telefone,
                email,
                sistema.alterado_em,
            ]
        )

    return response


def exportar_ods(request):
    response = HttpResponse(
        content_type="application/vnd.oasis.opendocument.spreadsheet .ods"
    )
    response[
        "Content-Disposition"
    ] = 'attachment; filename="dados-municipios-cadastrados-snc.ods"'

    workbook = xlwt.Workbook()
    planilha = workbook.add_sheet("SNC")
    preenche_planilha(planilha)

    workbook.save(response)

    return response


def exportar_xls(request):

    output = BytesIO()

    workbook = xlsxwriter.Workbook(output)
    planilha = workbook.add_worksheet("SNC")
    ultima_linha = preenche_planilha(planilha)

    planilha.autofilter(0, 0, ultima_linha, 16)
    workbook.close()
    output.seek(0)

    response = HttpResponse(output.read(), content_type="application/vnd.ms-excel")
    response[
        "Content-Disposition"
    ] = 'attachment; filename="dados-municipios-cadastrados-snc.xls"'

    return response


class CadastrarUsuario(TemplatedEmailFormViewMixin, CreateView):
    form_class = CadastrarUsuarioForm
    template_name = "usuario/cadastrar_usuario.html"
    success_url = reverse_lazy("adesao:sucesso_usuario")

    templated_email_template_name = "usuario"
    templated_email_from_email = "naoresponda@cultura.gov.br"

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    def templated_email_get_context_data(self, **kwargs):
        context = super().templated_email_get_context_data(**kwargs)
        context["object"] = self.object

        return context

    def templated_email_get_recipients(self, form):
        recipiente_list = [self.object.email, self.object.usuario.email_pessoal]

        return recipiente_list


@login_required
def selecionar_tipo_ente(request):
    return render(request, "prefeitura/selecionar_tipo_ente.html")


def sucesso_municipio(request):
    return render(request, "prefeitura/mensagem_sucesso_prefeitura.html")


class CadastrarSistemaCultura(TemplatedEmailFormViewMixin, CreateView):
    form_class = CadastrarSistemaCulturaForm
    model = SistemaCultura
    template_name = "cadastrar_sistema.html"
    success_url = reverse_lazy("adesao:sucesso_municipio")

    templated_email_template_name = "adesao"
    templated_email_from_email = "naoresponda@cultura.gov.br"


    def form_valid(self, form):
        context = self.get_context_data()

        form_sistema = context['form_sistema']
        form_sede = context['form_sede']
        form_gestor = context['form_gestor']

        if form_sistema.is_valid() and form_gestor.is_valid() and form_sede.is_valid():
            sede = form_sede.save()

            form_gestor.instance.tipo_funcionario = 2
            gestor = form_gestor.save()

            form_sistema.instance.sede = sede
            form_sistema.instance.gestor = gestor
            form_sistema.instance.cadastrador = self.request.user.usuario

            sistema = form_sistema.save()

            if not self.request.session.get('sistemas', False):
                self.request.session['sistemas'] = list()
                sistema_atualizado = SistemaCultura.sistema.get(ente_federado__id=sistema.ente_federado.id)
                atualiza_session(sistema_atualizado, self.request)
            else:
                if self.request.session.get('sistema_cultura_selecionado', False):
                    self.request.session['sistema_cultura_selecionado'].clear()
                    self.request.session.modified = True

            self.request.session['sistemas'].append({"id": sistema.id, "ente_federado__nome": sistema.ente_federado.nome})

            return super(CadastrarSistemaCultura, self).form_valid(form)
        else:
            return self.render_to_response(self.get_context_data(form=form))

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        context = super(CadastrarSistemaCultura, self).get_context_data(**kwargs)
        if self.request.POST:
            context['form_sistema'] = CadastrarSistemaCulturaForm(self.request.POST, self.request.FILES)
            context['form_sede'] = CadastrarSede(self.request.POST, self.request.FILES)
            context['form_gestor'] = CadastrarGestor(self.request.POST, self.request.FILES)
        else:
            context['form_sistema'] = CadastrarSistemaCulturaForm()
            context['form_sede'] = CadastrarSede()
            context['form_gestor'] = CadastrarGestor()
        return context

    def templated_email_get_recipients(self, form):
        gestor_pessoal = self.request.session['sistema_gestor']['email_pessoal']
        gestor_institucional = self.request.session['sistema_gestor']['email_institucional']
        recipiente_list = [self.request.user.email, self.request.user.usuario.email_pessoal,
            gestor_pessoal, gestor_institucional]

        return recipiente_list

    def templated_email_get_context_data(self, **kwargs):
        context = super().templated_email_get_context_data(**kwargs)
        context["object"] = self.object
        context["cadastrador"] = self.request.user.usuario
        context["sistema_atualizado"] = SistemaCultura.sistema.get(ente_federado__id=self.object.ente_federado.id)

        return context


class AlterarSistemaCultura(UpdateView):
    form_class = CadastrarSistemaCulturaForm
    model = SistemaCultura
    template_name = "cadastrar_sistema.html"

    def form_valid(self, form):
        context = self.get_context_data()
        form_sistema = context['form_sistema']
        form_sede = context['form_sede']
        form_gestor = context['form_gestor']

        if form_gestor.is_valid() and form_sede.is_valid() and form_sistema.is_valid():
            sede = form_sede.save()
            gestor = form_gestor.save()
            sistema = form_sistema.save()

            return redirect(self.get_success_url())
        else:
            return self.render_to_response(self.get_context_data(form=form))

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse_lazy("adesao:sucesso_municipio")

    def get_context_data(self, **kwargs):
        context = super(AlterarSistemaCultura, self).get_context_data(**kwargs)
        if self.request.POST:
            context['form_sistema'] = CadastrarSistemaCulturaForm(self.request.POST, self.request.FILES, instance=self.object)
            context['form_sede'] = CadastrarSede(self.request.POST, self.request.FILES, instance=self.object.sede)
            context['form_gestor'] = CadastrarGestor(self.request.POST, self.request.FILES, instance=self.object.gestor)
        else:
            context['form_sistema'] = CadastrarSistemaCulturaForm(instance=self.object)
            context['form_sede'] = CadastrarSede(instance=self.object.sede)
            context['form_gestor'] = CadastrarGestor(instance=self.object.gestor)

        return context


class CadastrarFuncionario(CreateView):
    form_class = CadastrarFuncionarioForm
    template_name = "cadastrar_funcionario.html"

    def get_sistema_cultura(self):
        return get_object_or_404(SistemaCultura, pk=int(self.kwargs['sistema']))

    def form_valid(self, form):
        sistema = self.get_sistema_cultura()
        setattr(sistema, 'gestor_cultura', form.save())
        sistema.save()

        sistema_atualizado = SistemaCultura.sistema.get(ente_federado__id=sistema.ente_federado.id)
        atualiza_session(sistema_atualizado, self.request)

        return super(CadastrarFuncionario, self).form_valid(form)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    def dispatch(self, *args, **kwargs):
        funcionario = getattr(self.get_sistema_cultura(), 'gestor_cultura')
        if funcionario:
            return redirect("adesao:alterar_funcionario", pk=funcionario.id)

        return super(CadastrarFuncionario, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('adesao:sucesso_funcionario')


class AlterarFuncionario(UpdateView):
    form_class = CadastrarFuncionarioForm
    model = Funcionario
    template_name = "cadastrar_funcionario.html"
    success_url = reverse_lazy("adesao:sucesso_funcionario")

    def form_valid(self, form):
        funcionario = form.instance

        if funcionario:
            sistema = getattr(funcionario, 'sistema_cultura_gestor_cultura').all().first()
            sistema.save()
            funcionario.save()

        sistema_atualizado = SistemaCultura.sistema.get(ente_federado__id=sistema.ente_federado.id)
        atualiza_session(sistema_atualizado, self.request)

        return super(AlterarFuncionario, self).form_valid(form)


class GeraPDF(WeasyTemplateView):

    def get_context_data(self, **kwargs):
        context = super(GeraPDF, self).get_context_data(**kwargs)
        context["request"] = self.request
        context["static"] = self.request.get_host()
        return context

    def get_pdf_filename(self):
        return self.kwargs['nome_arquivo']

    def get_template_names(self):
        return ['termos/%s.html' % self.kwargs['template']]


class ConsultarEnte(ListView):
    template_name = "consultar/consultar.html"
    paginate_by = "25"

    def get_queryset(self):
        tipo = self.kwargs['tipo']
        ente_federado = self.request.GET.get("ente_federado", None)

        sistemas = SistemaCultura.sistema.filter(estado_processo='6')

        if tipo == 'municipio':
            sistemas = sistemas.filter(ente_federado__cod_ibge__gt=100)
        elif tipo == 'estado':
            sistemas = sistemas.filter(ente_federado__cod_ibge__lte=100)

        if ente_federado:
            sistemas = sistemas.filter(ente_federado__nome__icontains=ente_federado)

        return sistemas


class RelatorioAderidos(ListView):
    template_name = "consultar/relatorio_aderidos.html"

    def get_queryset(self):

        # @TODO refatorar e usar relacionamentos diretamente do ORM django
        lista_uf = {}
        context = []

        # cria dict com estados, com estado_id como chave
        for uf in Uf.objects.order_by("sigla"):
            lista_uf[uf.codigo_ibge] = uf.sigla

        municipios_by_uf = (
            Municipio.objects.values("estado_id")
            .filter(usuario__estado_processo="6", cidade_id__isnull=False)
            .annotate(municipios_aderiram=Count("estado_id"))
        )

        for estado in municipios_by_uf:
            estado["uf_sigla"] = lista_uf[estado["estado_id"]]

            estado["total_municipios_uf"] = Cidade.objects.filter(
                uf_id=estado["estado_id"]
            ).count()

            estado["percent_mun_by_uf"] = round(
                ((estado["municipios_aderiram"] / estado["total_municipios_uf"]) * 100),
                2,
            )

            context.append(estado)

        return context


class Detalhar(DetailView):
    model = SistemaCultura
    template_name = "consultar/detalhar.html"

    def get_object(self):
        try:
            return SistemaCultura.sistema.get(ente_federado__cod_ibge=self.kwargs['cod_ibge'])
        except:
            raise Http404()

    def get_context_data(self, **kwargs):
        context = super(Detalhar, self).get_context_data(**kwargs)
        try:
            context["conselheiros"] = Conselheiro.objects.filter(conselho_id=self.object.conselho,
                situacao="1")
        except:
            context["conselheiros"] = None

        return context


class ConsultarPlanoTrabalhoMunicipio(ListView):
    template_name = "consultar/consultar.html"
    paginate_by = "25"

    def get_queryset(self):
        ente_federado = self.request.GET.get("municipio", None)

        if ente_federado:
            return Usuario.objects.filter(
                municipio__cidade__nome_municipio__icontains=ente_federado,
                estado_processo="6",
            )

        return Usuario.objects.filter(estado_processo="6").order_by(
            "municipio__cidade__nome_municipio"
        )


class ConsultarPlanoTrabalhoEstado(ListView):
    template_name = "consultar/consultar.html"
    paginate_by = "27"

    def get_queryset(self):
        ente_federado = self.request.GET.get("estado", None)

        if ente_federado:
            return Usuario.objects.filter(
                Q(municipio__cidade__isnull=True),
                Q(municipio__estado__nome_uf__icontains=ente_federado)
                | Q(municipio__estado__sigla__iexact=ente_federado),
            )

        return Usuario.objects.filter(
            municipio__estado__isnull=False, municipio__cidade__isnull=True
        )
