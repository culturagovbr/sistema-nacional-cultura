import csv
import xlwt
import xlsxwriter

from io import BytesIO
from datetime import timedelta
from threading import Thread

from django.shortcuts import render, redirect
from django.http import Http404, HttpResponse
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic import ListView, DetailView
from django.urls import reverse_lazy, reverse
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.template.loader import render_to_string
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db.models import Q, Count
from django.conf import settings

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
    SistemaCultura
)
from planotrabalho.models import Conselheiro, PlanoTrabalho
from adesao.forms import CadastrarUsuarioForm, CadastrarMunicipioForm
from adesao.forms import CadastrarResponsavelForm, CadastrarSecretarioForm
from adesao.utils import enviar_email_conclusao, verificar_anexo

from django_weasyprint import WeasyTemplateView


# Create your views here.
def index(request):
    if request.user.is_authenticated:
        return redirect("adesao:home")
    return render(request, "index.html")


def fale_conosco(request):
    return render(request, "fale_conosco.html")


@login_required
def home(request):
    ente_federado = request.user.usuario.municipio
    secretario = request.user.usuario.secretario
    responsavel = request.user.usuario.responsavel
    situacao = request.user.usuario.estado_processo
    historico = Historico.objects.filter(usuario=request.user.usuario)
    historico = historico.order_by("-data_alteracao")

    if request.user.is_staff:
        return redirect("gestao:acompanhar_adesao")

    if ente_federado and secretario and responsavel and int(situacao) < 1:
        request.user.usuario.estado_processo = "1"
        request.user.usuario.save()
        message_txt = render_to_string("conclusao_cadastro.txt", {"request": request})
        message_html = render_to_string(
            "conclusao_cadastro.email", {"request": request}
        )
        enviar_email_conclusao(request.user, message_txt, message_html)
    return render(request, "home.html", {"historico": historico})


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


def sucesso_responsavel(request):
    return render(request, "responsavel/mensagem_sucesso.html")


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
            "Cod.IBGE",
            "Situação",
            "Endereço",
            "Bairro",
            "CEP",
            "Telefone",
            "Email",
        ]
    )

    for sistema in SistemaCultura.sistema.all():
        if sistema.ente_federado:
            nome = sistema.ente_federado.nome
            cod_ibge = sistema.ente_federado.cod_ibge
        else:
            nome = "Nome não cadastrado"
            cod_ibge = "Código não cadastrado"

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
                cod_ibge,
                estado_processo,
                endereco,
                bairro,
                cep,
                telefone,
                email,
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
    planilha = workbook.add_worksheet("SNC")
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


class CadastrarUsuario(CreateView):
    form_class = CadastrarUsuarioForm
    template_name = "usuario/cadastrar_usuario.html"
    success_url = reverse_lazy("adesao:sucesso_usuario")

    def get_success_url(self):
        # TODO: Refatorar para usar django-templated-email
        Thread(
            target=send_mail,
            args=(
                "MINISTÉRIO DA CULTURA - SNC - CREDENCIAIS DE ACESSO",
                "Prezad@ "
                + self.object.usuario.nome_usuario
                + ",\n"
                + "Recebemos o seu cadastro no Sistema Nacional de Cultura. "
                + "Por favor confirme seu e-mail clicando no endereço abaixo:\n\n"
                + self.request.build_absolute_uri(
                    reverse(
                        "adesao:ativar_usuario",
                        args=[self.object.usuario.codigo_ativacao],
                    )
                )
                + "\n\n"
                + "Atenciosamente,\n\n"
                + "Equipe SNC\nMinistério da Cultura",
                "naoresponda@cultura.gov.br",
                [self.object.email],
            ),
            kwargs={"fail_silently": "False"},
        ).start()
        return super(CadastrarUsuario, self).get_success_url()


@login_required
def selecionar_tipo_ente(request):
    return render(request, "prefeitura/selecionar_tipo_ente.html")


def sucesso_municipio(request):
    return render(request, "prefeitura/mensagem_sucesso_prefeitura.html")


class CadastrarMunicipio(TemplatedEmailFormViewMixin, CreateView):
    form_class = CadastrarMunicipioForm
    model = Municipio
    template_name = "prefeitura/cadastrar_prefeitura.html"
    templated_email_template_name = "adesao"
    templated_email_from_email = "naoresponda@cultura.gov.br"
    success_url = reverse_lazy("adesao:sucesso_municipio")

    def templated_email_get_recipients(self, form):
        return [settings.RECEIVER_EMAIL]

    def get_context_data(self, **kwargs):
        context = super(CadastrarMunicipio, self).get_context_data(**kwargs)
        context["tipo_ente"] = self.kwargs["tipo_ente"]
        return context

    def templated_email_get_context_data(self, **kwargs):
        context = super().templated_email_get_context_data(**kwargs)
        context["object"] = self.object
        return context

    def form_valid(self, form):
        self.request.user.usuario.municipio = form.save()
        self.request.user.usuario.save()
        return super(CadastrarMunicipio, self).form_valid(form)

    def dispatch(self, *args, **kwargs):
        municipio = self.request.user.usuario.municipio
        if municipio:
            return redirect("adesao:alterar_municipio", pk=municipio.id)

        return super(CadastrarMunicipio, self).dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(CadastrarMunicipio, self).get_form_kwargs()
        kwargs["user"] = self.request.user.usuario
        return kwargs


class AlterarMunicipio(UpdateView):
    form_class = CadastrarMunicipioForm
    model = Municipio
    template_name = "prefeitura/cadastrar_prefeitura.html"
    success_url = reverse_lazy("adesao:sucesso_municipio")

    def dispatch(self, *args, **kwargs):
        municipio = self.request.user.usuario.municipio.pk
        if str(municipio) != self.kwargs["pk"]:
            raise Http404()

        return super(AlterarMunicipio, self).dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(AlterarMunicipio, self).get_form_kwargs()
        kwargs["user"] = self.request.user.usuario
        return kwargs


class CadastrarResponsavel(CreateView):
    form_class = CadastrarResponsavelForm
    template_name = "responsavel/cadastrar_responsavel.html"
    success_url = reverse_lazy("adesao:sucesso_responsavel")

    def form_valid(self, form):
        self.request.user.usuario.responsavel = form.save()
        self.request.user.usuario.save()
        return super(CadastrarResponsavel, self).form_valid(form)

    def dispatch(self, *args, **kwargs):
        responsavel = self.request.user.usuario.responsavel
        if responsavel:
            return redirect("adesao:alterar_responsavel", pk=responsavel.id)

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
        responsavel.email_institucional_responsavel = (
            secretario.email_institucional_secretario
        )
        try:
            responsavel.full_clean()
            responsavel.save()
        except ValidationError:
            return redirect("adesao:responsavel")
        request.user.usuario.responsavel = responsavel
        request.user.usuario.save()
    return redirect("adesao:responsavel")


class AlterarResponsavel(UpdateView):
    form_class = CadastrarResponsavelForm
    model = Responsavel
    template_name = "responsavel/cadastrar_responsavel.html"
    success_url = reverse_lazy("adesao:sucesso_responsavel")


def sucesso_secretario(request):
    return render(request, "secretario/mensagem_sucesso_secretario.html")


class CadastrarSecretario(CreateView):
    form_class = CadastrarSecretarioForm
    template_name = "secretario/cadastrar_secretario.html"
    success_url = reverse_lazy("adesao:sucesso_secretario")

    def form_valid(self, form):
        self.request.user.usuario.secretario = form.save()
        self.request.user.usuario.save()
        return super(CadastrarSecretario, self).form_valid(form)

    def dispatch(self, *args, **kwargs):
        secretario = self.request.user.usuario.secretario
        if secretario:
            return redirect("adesao:alterar_secretario", pk=secretario.id)

        return super(CadastrarSecretario, self).dispatch(*args, **kwargs)


class AlterarSecretario(UpdateView):
    form_class = CadastrarSecretarioForm
    model = Secretario
    template_name = "secretario/cadastrar_secretario.html"
    success_url = reverse_lazy("adesao:sucesso_secretario")


class MinutaAcordo(WeasyTemplateView):
    pdf_filename = "minuta_acordo.pdf"
    template_name = "termos/minuta_acordo.html"

    def get_context_data(self, **kwargs):
        context = super(MinutaAcordo, self).get_context_data(**kwargs)
        context["request"] = self.request
        context["static"] = self.request.get_host()
        return context


class TermoSolicitacao(WeasyTemplateView):
    pdf_filename = "solicitacao.pdf"
    template_name = "termos/solicitacao.html"

    def get_context_data(self, **kwargs):
        context = super(TermoSolicitacao, self).get_context_data(**kwargs)
        context["request"] = self.request
        context["static"] = self.request.get_host()
        return context


class OficioAlteracao(WeasyTemplateView):
    pdf_filename = "alterar_responsavel.pdf"
    template_name = "termos/alterar_responsavel.html"

    def get_context_data(self, **kwargs):
        context = super(OficioAlteracao, self).get_context_data(**kwargs)
        context["request"] = self.request
        context["static"] = self.request.get_host()
        return context


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
