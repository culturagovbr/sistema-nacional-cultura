from threading import Thread

from django.contrib.contenttypes.models import ContentType
from django.core.mail import send_mail

from django.db.models import Q

from django.shortcuts import redirect
from django.shortcuts import render
from django.shortcuts import get_object_or_404

from django.http import Http404, JsonResponse, HttpResponseRedirect
from django.http import JsonResponse
from django.http import HttpResponseRedirect

from django.contrib.auth.models import User

from django.views.generic import CreateView
from django.views.generic import DetailView
from django.views.generic import ListView

from django.views.generic.edit import FormView
from django.views.generic.edit import UpdateView

from django.urls import reverse_lazy

from dal import autocomplete

from adesao.models import Usuario
from adesao.models import Cidade
from adesao.models import Municipio
from adesao.models import Historico

from planotrabalho.models import PlanoTrabalho
from planotrabalho.models import CriacaoSistema
from planotrabalho.models import PlanoCultura
from planotrabalho.models import FundoCultura
from planotrabalho.models import OrgaoGestor
from planotrabalho.models import ConselhoCultural
from planotrabalho.models import SituacoesArquivoPlano

from gestao.utils import enviar_email_aprovacao_plano

from adesao.models import Usuario
from adesao.models import Cidade
from adesao.models import Uf
from adesao.models import Municipio
from adesao.models import Historico

from planotrabalho.models import CriacaoSistema
from planotrabalho.models import PlanoCultura
from planotrabalho.models import FundoCultura
from planotrabalho.models import OrgaoGestor
from planotrabalho.models import ConselhoCultural
from planotrabalho.models import SituacoesArquivoPlano

from .forms import AlterarSituacao, DiligenciaForm, AlterarDocumentosEnteFederadoForm, InserirSEI
from .forms import AlterarCadastradorForm, AlterarUsuarioForm, AlterarOrgaoForm
from .forms import AlterarFundoForm, AlterarPlanoForm, AlterarConselhoForm, AlterarSistemaForm

from .forms import AlterarCadastradorForm
from .forms import AlterarUsuarioForm
from .forms import AlterarOrgaoForm

from .forms import AlterarFundoForm
from .forms import AlterarPlanoForm
from .forms import AlterarConselhoForm
from .forms import AlterarSistemaForm


# Acompanhamento das adesões
class AlterarCadastrador(FormView):
    """AlterarCadastrador
    Altera o cadastrador de um Municipio aderido
    """
    template_name = 'gestao/alterar_cadastrador.html'
    form_class = AlterarCadastradorForm
    success_url = reverse_lazy('gestao:acompanhar_adesao')

    def form_valid(self, form):
        form.save()
        return super(AlterarCadastrador, self).form_valid(form)


class AlterarCadastradorEstado(FormView):
    """AlterarCadastradorEstado
    Altera o cadastrador de um Estado aderido
    """
    template_name = 'gestao/alterar_cadastrador_estado.html'
    # form_class = AlterarCadastradorForm
    success_url = reverse_lazy('gestao:acompanhar_adesao')

    def form_valid(self, form):
        form.save()
        return super(AlterarCadastradorEstado, self).form_valid(form)


class CidadeChain(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        """ Filtra todas as cidade de uma determinada UF """

        uf_pk = self.forwarded.get('estado', None)
        if uf_pk:
            choices = Cidade.objects\
                .filter(uf__pk=uf_pk)\
                .values_list('pk', 'nome_municipio', named=True)
        else:
            choices = Cidade.objects\
                .filter(uf__sigla__iexact=self.q)\
                .values_list('pk', 'nome_municipio', named=True)
        return choices

    def get_result_label(self, item):
        return item.nome_municipio

    def get_selected_result_label(self, item):
        return item.nome_municipio


class UfChain(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        """ Filtra todas as uf passando nome ou sigla """

        choices = Uf.objects.filter(
                    Q(sigla__iexact=self.q) | Q(nome_uf__icontains=self.q)
                ).values_list('pk', 'sigla', named=True)
        return choices

    def get_result_label(self, item):
        return item.sigla

    def get_selected_result_label(self, item):
        return item.sigla


def alterar_situacao(request, id):
    if request.method == "POST":
        form = AlterarSituacao(
            request.POST,
            instance=Usuario.objects.get(id=id))
        if form.is_valid():
            form.save()

            # try:
            #     usuario = Usuario.objects.get(
            #         id=id, plano_trabalho__criacao_sistema__situacao_lei_sistema_id='2',
            #         plano_trabalho__conselho_cultural__situacao_ata_id='2',
            #         plano_trabalho__fundo_cultura__situacao_lei_plano_id='2',
            #         plano_trabalho__orgao_gestor__situacao_relatorio_secretaria_id='2',
            #         plano_trabalho__plano_cultura__situacao_lei_plano_id='2')
            #     usuario = User.objects.get(id=usuario.user_id)
            #
            #     message_txt = render('emails/aprovacao_plano.txt')
            #     message_html = render('emails/aprovacao_plano.email')
            #     enviar_email_aprovacao_plano(usuario, message_txt, message_html)
            # except Exception as e:
            #     return redirect('gestao:detalhar', pk=id)

    return redirect('gestao:detalhar', pk=id)

def inserir_sei(request, id):
    if request.method == "POST":
        form = InserirSEI(
            request.POST,
            instance=Usuario.objects.get(id=id))
        if form.is_valid():
            form.save()

    return redirect('gestao:detalhar', pk=id)

def ajax_cadastrador_cpf(request):
    if request.method == "POST":
        try:
            ente_federado = request.POST.get("ente_federado", None)
            estado = request.POST.get("estado", None)

            if estado:
                municipio = Municipio.objects.get(cidade__isnull=True, estado_id=ente_federado)
            else:
                municipio = Municipio.objects.get(cidade=ente_federado)

            usuario = Usuario.objects.get(municipio_id=municipio.id)
            user = User.objects.get(id=usuario.user_id)
            if usuario.data_publicacao_acordo:
                data_de_publicacao = usuario.data_publicacao_acordo.strftime('%d/%m/%Y')
            else:
                data_de_publicacao = None

            data = {
                'cpf': user.username,
                'data_publicacao_acordo': data_de_publicacao,
                'estado_processo': usuario.estado_processo
                }
            return JsonResponse(data)

        except:
            return JsonResponse(data={"erro": True})
    else:
        return JsonResponse(data={"erro": True})


class AcompanharPrazo(ListView):
    template_name = 'gestao/acompanhar_prazo.html'
    paginate_by = 10

    def get_queryset(self):
        ente_federado = self.request.GET.get('municipio', None)
        if ente_federado:
            municipio = Usuario.objects.filter(
                municipio__cidade__nome_municipio__icontains=ente_federado).order_by('municipio__estado__nome_uf')
            estado = Usuario.objects.filter(
                municipio__cidade__isnull=True,
                municipio__estado__nome_uf__icontains=ente_federado).order_by('municipio__estado__nome_uf')

            return municipio | estado
        return Usuario.objects.filter(estado_processo='6', data_publicacao_acordo__isnull=False).order_by(
            'municipio__estado__nome_uf')


def aditivar_prazo(request, id):
    if request.method == "POST":
        user = Usuario.objects.get(id=id)
        user.prazo = user.prazo + 1
        user.save()

    return redirect('gestao:acompanhar_prazo')


class AcompanharAdesao(ListView):
    template_name = 'gestao/adesao/acompanhar.html'
    paginate_by = 10

    def get_queryset(self):
        situacao = self.request.GET.get('situacao', None)
        ente_federado = self.request.GET.get('municipio', None)

        if situacao in ('0', '1', '2', '3', '4', '5', '6'):
            return Municipio.objects.filter(usuario__estado_processo=situacao)

        if ente_federado:
            municipio = Municipio.objects.filter(
                cidade__nome_municipio__icontains=ente_federado)
            estado = Municipio.objects.filter(
                cidade__nome_municipio__isnull=True,
                estado__nome_uf__icontains=ente_federado)

            return municipio | estado

        return Municipio.objects.all()


# Acompanhamento dos planos de trabalho
def diligencia_documental(request, etapa, st, id):
    usuario = Usuario.objects.get(id=id)
    #print(getattr(getattr(usuario.plano_trabalho, etapa), st))
    #modificando o comportamento pois, no caso da "SituacoesArquivoPlano" agora é um objeto, e não só um valor 0 na tabela
    if isinstance(getattr(getattr(usuario.plano_trabalho, etapa), st), SituacoesArquivoPlano):
        usuario.plano_trabalho.criacao_sistema.situacao_lei_sistema = SituacoesArquivoPlano.objects.get(pk=0)
    else:
        setattr(getattr(usuario.plano_trabalho, etapa), st, 0)
    form = DiligenciaForm()
    if request.method == 'POST':
        form = DiligenciaForm(request.POST, usuario=usuario)
        if form.is_valid():
            getattr(usuario.plano_trabalho, etapa).save()
            form.save()
        return redirect('gestao:acompanhar_adesao')
    return render(
        request,
        'gestao/planotrabalho/diligencia.html',
        {'form': form, 'etapa': etapa, 'st': st, 'id': id})


def concluir_etapa(request, etapa, st, id):
    usuario = Usuario.objects.get(id=id)
    if isinstance(getattr(getattr(usuario.plano_trabalho, etapa), st), SituacoesArquivoPlano):
        usuario.plano_trabalho.criacao_sistema.situacao_lei_sistema = SituacoesArquivoPlano.objects.get(pk=2)
    else:
        setattr(getattr(usuario.plano_trabalho, etapa), st, 2)
    getattr(usuario.plano_trabalho, etapa).save()
    return redirect('gestao:detalhar', pk=id)


def situacao_3 (request, etapa, st, id):
    usuario = Usuario.objects.get(id=id)
    setattr(getattr(usuario.plano_trabalho, etapa), st, 3)
    getattr(usuario.plano_trabalho, etapa).save()
    return redirect('gestao:detalhar', pk=id)

def situacao_4 (request, etapa, st, id):
    usuario = Usuario.objects.get(id=id)
    setattr(getattr(usuario.plano_trabalho, etapa), st, 4)
    getattr(usuario.plano_trabalho, etapa).save()
    return redirect('gestao:detalhar', pk=id)

def situacao_5 (request, etapa, st, id):
    usuario = Usuario.objects.get(id=id)
    setattr(getattr(usuario.plano_trabalho, etapa), st, 5)
    getattr(usuario.plano_trabalho, etapa).save()
    return redirect('gestao:detalhar', pk=id)

def situacao_6 (request, etapa, st, id):
    usuario = Usuario.objects.get(id=id)
    setattr(getattr(usuario.plano_trabalho, etapa), st, 6)
    getattr(usuario.plano_trabalho, etapa).save()
    return redirect('gestao:detalhar', pk=id)

#Teste Christian

class AcompanharSistema(ListView):
    template_name = 'gestao/planotrabalho/acompanhar_sistema.html'
    paginate_by = 10

    def get_queryset(self):
        anexo = self.request.GET.get('anexo', None)
        q = self.request.GET.get('q', None)
        if not anexo:
            raise Http404()
        usuarios = Usuario.objects.filter(estado_processo='6')
        usuarios = usuarios.exclude(plano_trabalho__criacao_sistema=None)

        if anexo == 'lei_sistema_cultura':
            usuarios = usuarios.filter(
                plano_trabalho__criacao_sistema__situacao=1)
            usuarios = usuarios.exclude(
                plano_trabalho__criacao_sistema__lei_sistema_cultura='')
        else:
            raise Http404()

        if q:
            usuarios = usuarios.filter(
                municipio__cidade__nome_municipio__icontains=q)

        return usuarios


class AcompanharOrgao(ListView):
    template_name = 'gestao/planotrabalho/acompanhar_orgao.html'
    paginate_by = 10

    def get_queryset(self):
        q = self.request.GET.get('q', None)
        usuarios = Usuario.objects.filter(estado_processo='6')
        usuarios = usuarios.exclude(plano_trabalho__orgao_gestor=None)
        usuarios = usuarios.filter(
            plano_trabalho__orgao_gestor__situacao=1)
        usuarios = usuarios.exclude(
            plano_trabalho__orgao_gestor__relatorio_atividade_secretaria='')
        if q:
            usuarios = usuarios.filter(
                municipio__cidade__nome_municipio__icontains=q)
        return usuarios


class AcompanharConselho(ListView):
    template_name = 'gestao/planotrabalho/acompanhar_conselho.html'
    paginate_by = 10

    def get_queryset(self):
        q = self.request.GET.get('q', None)
        usuarios = Usuario.objects.filter(estado_processo='6')
        usuarios = usuarios.exclude(plano_trabalho__conselho_cultural=None)
        usuarios = usuarios.filter(
            plano_trabalho__conselho_cultural__situacao=1)
        usuarios = usuarios.exclude(
            plano_trabalho__conselho_cultural__ata_regimento_aprovado='')
        if q:
            usuarios = usuarios.filter(
                municipio__cidade__nome_municipio__icontains=q)
        return usuarios


class AcompanharFundo(ListView):
    template_name = 'gestao/planotrabalho/acompanhar_fundo.html'
    paginate_by = 10

    def get_queryset(self):
        q = self.request.GET.get('q', None)
        usuarios = Usuario.objects.filter(estado_processo='6')
        usuarios = usuarios.exclude(plano_trabalho__fundo_cultura=None)
        usuarios = usuarios.filter(
            plano_trabalho__fundo_cultura__situacao=1)
        usuarios = usuarios.exclude(
            plano_trabalho__fundo_cultura__lei_fundo_cultura='')
        if q:
            usuarios = usuarios.filter(
                municipio__cidade__nome_municipio__icontains=q)
        return usuarios


class AcompanharPlano(ListView):
    template_name = 'gestao/planotrabalho/acompanhar_plano.html'
    paginate_by = 10

    def get_queryset(self):
        anexo = self.request.GET.get('anexo', None)
        q = self.request.GET.get('q', None)
        if not anexo:
            raise Http404()
        usuarios = Usuario.objects.filter(estado_processo='6')
        usuarios = usuarios.exclude(plano_trabalho__plano_cultura=None)

        if anexo == 'lei_plano_cultura':
            usuarios = usuarios.filter(
                plano_trabalho__plano_cultura__situacao=1)
            usuarios = usuarios.exclude(
                plano_trabalho__plano_cultura__lei_plano_cultura='')
        else:
            raise Http404()

        if q:
            usuarios = usuarios.filter(
                municipio__cidade__nome_municipio__icontains=q)

        return usuarios

#Teste Christian


class DetalharUsuario(DetailView):
    model = Usuario
    template_name = 'gestao/detalhe_municipio.html'

    def get_context_data(self, **kwargs):
        context = super(DetalharUsuario, self).get_context_data(**kwargs)
        situacao = context['usuario'].estado_processo
        context['processo_sei'] = context['usuario'].processo_sei

        try:

            if situacao == '3':
                historico = Historico.objects.filter(usuario_id=context['usuario'].id)
                historico = historico[0]
                context['dado_situacao'] = historico.descricao

            elif situacao == '2':
                municipio = Municipio.objects.get(usuario__id=context['usuario'].id)
                context['dado_situacao'] = municipio.localizacao

            elif situacao == '4':
                municipio = Municipio.objects.get(usuario__id=context['usuario'].id)
                context['dado_situacao'] = municipio.numero_processo

            elif situacao == '6':
                context['dado_situacao'] = context['usuario'].data_publicacao_acordo.strftime('%d/%m/%Y')
                context['link_publicacao'] = context['usuario'].link_publicacao_acordo
        except:
            pass
        return context


class ListarUsuarios(ListView):
    model = Usuario
    template_name = 'gestao/listar_usuarios.html'
    paginate_by = 10

    def get_queryset(self):
        q = self.request.GET.get('q', None)
        usuarios = Usuario.objects.all()

        if q:
            usuarios = usuarios.filter(Q(user__username__icontains=q) | Q(user__email__icontains=q))

        return usuarios


class AlterarUsuario(UpdateView):
    model = User
    form_class = AlterarUsuarioForm
    template_name = 'gestao/listar_usuarios.html'
    success_url = reverse_lazy('gestao:usuarios')

    def get_success_url(self):
        return reverse_lazy('gestao:usuarios')


class ListarDocumentosEnteFederado(ListView):
    template_name = 'gestao/inserir_documentos/inserir_entefederado.html'
    paginate_by = 10

    def get_queryset(self):
        situacao = self.request.GET.get('situacao', None)
        ente_federado = self.request.GET.get('municipio', None)

        if situacao in ('1', '2', '3', '4', '5'):
            return Municipio.objects.filter(usuario__estado_processo=situacao)

        if ente_federado:
            municipio = Municipio.objects.filter(
                cidade__nome_municipio__icontains=ente_federado)
            estado = Municipio.objects.filter(
                cidade__nome_municipio__isnull=True,
                estado__nome_uf__icontains=ente_federado)

            return municipio | estado

        return Municipio.objects.filter(usuario__estado_processo__range=('1', '5'))


class AlterarDocumentosEnteFederado(UpdateView):

    template_name = 'gestao/inserir_documentos/alterar_entefederado.html'
    form_class = AlterarDocumentosEnteFederadoForm
    model = Municipio

    def get_success_url(self):
        return reverse_lazy('gestao:inserir_entefederado')


class InserirSistema(ListView):
    template_name = 'gestao/inserir_documentos/inserir_sistema.html'
    paginate_by = 10

    def get_queryset(self):
        q = self.request.GET.get('q', None)

        usuarios = Usuario.objects.filter(estado_processo='6')
        usuarios = usuarios.exclude(plano_trabalho__criacao_sistema=None)

        if q:
            usuarios = usuarios.filter(
                municipio__cidade__nome_municipio__icontains=q)

        return usuarios


class AlterarSistema(UpdateView):
    template_name = 'gestao/inserir_documentos/alterar_sistema.html'
    form_class = AlterarSistemaForm
    model = CriacaoSistema

    def get_success_url(self):
        return reverse_lazy('gestao:inserir_sistema')


class InserirOrgao(ListView):
    template_name = 'gestao/inserir_documentos/inserir_orgao.html'
    paginate_by = 10

    def get_queryset(self):
        q = self.request.GET.get('q', None)
        usuarios = Usuario.objects.filter(estado_processo='6')
        usuarios = usuarios.exclude(plano_trabalho__orgao_gestor=None)

        if q:
            usuarios = usuarios.filter(
                municipio__cidade__nome_municipio__icontains=q)
        return usuarios


class AlterarOrgao(UpdateView):
    template_name = 'gestao/inserir_documentos/alterar_orgao.html'
    form_class = AlterarOrgaoForm
    model = OrgaoGestor

    def get_success_url(self):
        return reverse_lazy('gestao:inserir_orgao')


class InserirConselho(ListView):
    template_name = 'gestao/inserir_documentos/inserir_conselho.html'
    paginate_by = 10

    def get_queryset(self):
        q = self.request.GET.get('q', None)
        usuarios = Usuario.objects.filter(estado_processo='6')
        usuarios = usuarios.exclude(plano_trabalho__conselho_cultural=None)

        if q:
            usuarios = usuarios.filter(
                municipio__cidade__nome_municipio__icontains=q)
        return usuarios


class AlterarConselho(UpdateView):
    template_name = 'gestao/inserir_documentos/alterar_conselho.html'
    form_class = AlterarConselhoForm
    model = ConselhoCultural

    def get_success_url(self):
        return reverse_lazy('gestao:inserir_conselho')


class InserirFundo(ListView):
    template_name = 'gestao/inserir_documentos/inserir_fundo.html'
    paginate_by = 10

    def get_queryset(self):
        q = self.request.GET.get('q', None)
        usuarios = Usuario.objects.filter(estado_processo='6')
        usuarios = usuarios.exclude(plano_trabalho__fundo_cultura=None)

        if q:
            usuarios = usuarios.filter(
                municipio__cidade__nome_municipio__icontains=q)
        return usuarios


class AlterarFundo(UpdateView):
    template_name = 'gestao/inserir_documentos/alterar_fundo.html'
    form_class = AlterarFundoForm
    model = FundoCultura

    def get_success_url(self):
        return reverse_lazy('gestao:inserir_fundo')


class InserirPlano(ListView):
    template_name = 'gestao/inserir_documentos/inserir_plano.html'
    paginate_by = 10

    def get_queryset(self):
        q = self.request.GET.get('q', None)
        usuarios = Usuario.objects.filter(estado_processo='6')
        usuarios = usuarios.exclude(plano_trabalho__plano_cultura=None)

        if q:
            usuarios = usuarios.filter(
                municipio__cidade__nome_municipio__icontains=q)

        return usuarios


class AlterarPlano(UpdateView):
    template_name = 'gestao/inserir_documentos/alterar_plano.html'
    form_class = AlterarPlanoForm
    model = PlanoCultura

    def get_success_url(self):
        return reverse_lazy('gestao:inserir_plano')


class Prorrogacao(ListView):
    template_name = 'gestao/prorrogacao/listar_prorrogacao.html'
    paginate_by = 10

    def get_queryset(self):
        q = self.request.GET.get('q', None)
        usuarios = Usuario.objects.filter(estado_processo='6')

        usuarios = usuarios.exclude(
            plano_trabalho__conselho_cultural=None,
            plano_trabalho__criacao_sistema=None,
            plano_trabalho__fundo_cultura=None,
            plano_trabalho__orgao_gestor=None,
            plano_trabalho__plano_cultura=None)

        if q:
            usuarios = usuarios.filter(
                municipio__cidade__nome_municipio__icontains=q)
        return usuarios


class DiligenciaView(CreateView):
    template_name = 'gestao/diligencia/diligencia.html'
    form_class = DiligenciaForm

    componentes = {
        'fundo_cultura': 'fundocultura',
        'orgao_gestor': 'orgaogestor',
        'conselho_cultural': 'conselhocultural',
        'plano_cultura': 'planocultura',
        'criacao_sistema': 'criacaosistema',
        'plano_trabalho': 'planotrabalho',
    }

    def send_email_diligencia(self):
        usuario = self.get_plano_trabalho().usuario
        situacoes = self.get_situacao_componentes()
        send_mail('MINISTÉRIO DA CULTURA - SNC - DILIGÊNCIA PLANO DE TRABALHO',
                  'Prezado Cadastrador,\n' +
                  'Uma diligência referente ao Plano de Trabalho do ente federado ' + self.get_ente_federado_name() +
                  ' acabou de ser realizada.\n' +
                  'O corpo da mensagem é: ' + self.object.texto_diligencia + '\n' +
                  'As situações dos arquivos enviados de cada componente são: \n' +
                  'Lei de Criação do Sistema de Cultura: ' + situacoes['criacao_sistema'] + ';\n' +
                  'Órgão Gestor: ' + situacoes['orgao_gestor'] + ';\n' +
                  'Conselho de Política Cultural: ' + situacoes['conselho_cultural'] + ';\n' +
                  'Fundo de Cultura: ' + situacoes['fundo_cultura'] + ';\n' +
                  'Plano de Cultura: ' + situacoes['plano_cultura'] + '.\n\n' +
                  'Atenciosamente,\n\n' +
                  'Equipe SNC\nMinistério da Cultura',
                  'naoresponda@cultura.gov.br',
                  [usuario.user.email], fail_silently=False)

    def get_success_url(self):
        usuario = self.get_plano_trabalho().usuario
        return reverse_lazy('gestao:detalhar', kwargs={'pk': usuario.id})

    def get_plano_trabalho(self):
        return get_object_or_404(PlanoTrabalho, pk=int(self.kwargs['pk']))

    def get_ente_federado(self):
        plano_trabalho = self.get_plano_trabalho()
        return plano_trabalho.usuario.municipio

    def get_form(self):
        form_class = super().get_form_class()

        return form_class(resultado=self.kwargs['resultado'], componente=self.kwargs['componente'], **self.get_form_kwargs())

    def get_componente(self):
        """ Retonar o componente baseado no argumento passado pela url"""
        plano_trabalho = self.get_plano_trabalho()
        plano_componente = None

        if(self.kwargs['componente'] != 'plano_trabalho'):
            try:
                plano_componente = getattr(plano_trabalho,
                                           self.kwargs['componente'])
                assert plano_componente
            except(AssertionError, AttributeError):
                raise Http404('Componente não existe')
        else:
            plano_componente = plano_trabalho

        return plano_componente

    def get_ente_federado_name(self):
        ente_federado = self.get_ente_federado()
        name = None

        if ente_federado.cidade:
            name = "{} - {}".format(ente_federado.cidade.nome_municipio,
                                    ente_federado.estado.sigla)

        else:
            name = ente_federado.estado.sigla

        return name

    def get_historico_diligencias(self):
        plano_componente = self.get_componente()

        historico_diligencias = plano_componente.diligencias.all().order_by('-data_criacao').order_by('-id')

        return historico_diligencias[:3]

    def get_componente_descricao(self, componente):
        try:
            descricao = componente.situacao.descricao
        except AttributeError:
            descricao = 'Inexistente'

        return descricao

    def get_situacao_componentes(self):
        situacoes = {}
        plano_trabalho = self.get_plano_trabalho()

        componentes = ["criacao_sistema", "orgao_gestor", "fundo_cultura", "conselho_cultural", "plano_cultura"]

        for componente in componentes:
            plano_comp = getattr(plano_trabalho, componente)
            situacoes[componente] = self.get_componente_descricao(plano_comp)

        return situacoes

    def get_context_data(self, form=None, **kwargs):
        context = {}
        plano_componente = self.get_componente()
        ente_federado = self.get_ente_federado()

        if form is None:
            form = self.get_form()

        if (isinstance(plano_componente, PlanoTrabalho)):
            context['situacoes'] = self.get_situacao_componentes()
        else:
            context['arquivo'] = plano_componente.arquivo

        context['form'] = form
        context['ente_federado'] = self.get_ente_federado_name()
        context['historico_diligencias'] = self.get_historico_diligencias()
        context['usuario_id'] = ente_federado.usuario.id
        context['data_envio'] = "--/--/----"
        context['componente'] = plano_componente
        context['plano_trabalho'] = self.get_plano_trabalho()

        return context

    def form_valid(self, form):
        plano_componente = self.get_componente()
        self.object = form.save()

        plano_componente.situacao = self.object.classificacao_arquivo
        plano_componente.save()

        if(isinstance(self.get_componente(), PlanoTrabalho)):
            self.send_email_diligencia()

        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form), status=400)

    def post(self, request, *args, **kwargs):
        plano_componente = self.get_componente()
        form = self.get_form()

        if(isinstance(plano_componente, PlanoTrabalho)):
            form.instance.tipo_diligencia = 'geral'
        else:
            form.instance.tipo_diligencia = 'componente'

        form.instance.usuario = request.user.usuario
        form.instance.ente_federado = self.get_ente_federado()
        form.instance.componente_id = plano_componente.id
        form.instance.componente_type = ContentType.objects.get(app_label='planotrabalho', model=self.componentes[self.kwargs['componente']])

        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)








