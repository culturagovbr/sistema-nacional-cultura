from threading import Thread
from itertools import chain

from django.contrib.contenttypes.models import ContentType
from django.core.mail import send_mail

from django.db.models import Case, When, DateField, Count, Q
from django.db.models.functions import Least

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

from templated_email.generic_views import TemplatedEmailFormViewMixin

from adesao.models import Usuario
from adesao.models import Cidade
from adesao.models import Municipio
from adesao.models import Historico
from adesao.models import SistemaCultura

from planotrabalho.models import PlanoTrabalho
from planotrabalho.models import CriacaoSistema
from planotrabalho.models import PlanoCultura
from planotrabalho.models import FundoCultura
from planotrabalho.models import OrgaoGestor
from planotrabalho.models import ConselhoCultural
from planotrabalho.models import SituacoesArquivoPlano
from planotrabalho.models import Componente

from gestao.utils import enviar_email_aprovacao_plano
from gestao.utils import empty_to_none

from adesao.models import Uf

from .models import DiligenciaSimples

from .forms import DiligenciaComponenteForm, DiligenciaGeralForm, AlterarDocumentosEnteFederadoForm
from .forms import AlterarDadosAdesao

from .forms import AlterarCadastradorForm
from .forms import AlterarUsuarioForm
from .forms import AlterarOrgaoForm

from .forms import AlterarFundoForm
from .forms import AlterarPlanoForm
from .forms import AlterarConselhoForm
from .forms import AlterarSistemaForm
from .forms import CriarSistemaForm
from .forms import CriarOrgaoForm
from .forms import CriarConselhoForm
from .forms import CriarFundoForm
from .forms import CriarPlanoForm


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


class CidadeChain(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        """ Filtra todas as cidade de uma determinada UF """

        uf_pk = self.forwarded.get('estado', None)

        if uf_pk:
            choices = Cidade.objects\
                .filter(Q(uf__pk=uf_pk) & Q(nome_municipio__icontains=self.q))\
                .values_list('pk', 'nome_municipio', named=True)
        else:
            choices = Cidade.objects\
                .filter(uf__sigla__iexact=self.q)\
                .values_list('pk', 'nome_municipio', named=True)
        return choices

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


def alterar_dados_adesao(request, pk):
    if request.method == "POST":
        form = AlterarDadosAdesao(request.POST,
                                  instance=Usuario.objects.get(pk=pk))
        if form.is_valid():
            form.save()
    return redirect('gestao:detalhar', pk=pk)


def ajax_cadastrador_cpf(request):
    if request.method == "GET":
        try:
            cidade_id = empty_to_none(request.GET.get("municipio", None))
            estado_id = empty_to_none(request.GET.get("estado", None))

            ente_federado = Municipio.objects.get(cidade=cidade_id, estado=estado_id)
            usuario = ente_federado.usuario

            data = {
                'cpf': usuario.user.username,
                'data_publicacao_acordo': usuario.data_publicacao_acordo,
                'estado_processo': usuario.estado_processo
                }
            return JsonResponse(status=200, data=data)

        except Municipio.DoesNotExist:
            return JsonResponse(status=400, data={"erro": "Município não existe"})
    else:
        return JsonResponse(status=415, data={"erro": "Método não permitido"})


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

    def annotate_componente_mais_antigo_por_situacao(self, componentes, *args):
        componentes = componentes.annotate(
            data_lei_sem_analise=Case(
                When(usuario__plano_trabalho__criacao_sistema__situacao__in=args, then='usuario__plano_trabalho__criacao_sistema__data_envio'),
                default=None,
                output_field=DateField(),
            ),
             data_orgao_sem_analise=Case(
                When(usuario__plano_trabalho__orgao_gestor__situacao__in=args, then='usuario__plano_trabalho__orgao_gestor__data_envio'),
                default=None,
                output_field=DateField(),
            ),
             data_conselho_sem_analise=Case(
                When(usuario__plano_trabalho__conselho_cultural__situacao__in=args, then='usuario__plano_trabalho__conselho_cultural__data_envio'),
                default=None,
                output_field=DateField(),
            ),
             data_plano_sem_analise=Case(
                When(usuario__plano_trabalho__plano_cultura__situacao__in=args, then='usuario__plano_trabalho__plano_cultura__data_envio'),
                default=None,
                output_field=DateField(),
            ),
            data_fundo_sem_analise=Case(
                When(usuario__plano_trabalho__fundo_cultura__situacao__in=args, then='usuario__plano_trabalho__fundo_cultura__data_envio'),
                default=None,
                output_field=DateField(),
            )
        ).annotate(
            mais_antigo=Least('data_lei_sem_analise', 'data_orgao_sem_analise', 'data_conselho_sem_analise', 'data_plano_sem_analise',
                'data_fundo_sem_analise')
        )

        return componentes


    def get_queryset(self):
        situacao = self.request.GET.get('situacao', None)
        ente_federado = self.request.GET.get('municipio', None)

        if situacao in ('0', '1', '2', '3', '4', '5', '6'):
            entes = Municipio.objects.filter(usuario__estado_processo=situacao)

        elif ente_federado:
            municipio = Municipio.objects.filter(
                cidade__nome_municipio__icontains=ente_federado)
            estado = Municipio.objects.filter(
                cidade__nome_municipio__isnull=True,
                estado__nome_uf__icontains=ente_federado)

            entes = municipio | estado

        else:
            entes = Municipio.objects.all()

        entes_concluidos = self.annotate_componente_mais_antigo_por_situacao(entes, 2, 3).annotate(
            cadastrador=Count('usuario')).order_by('-cadastrador', '-usuario__estado_processo', 'mais_antigo')

        entes_diligencia = self.annotate_componente_mais_antigo_por_situacao(entes, 4, 5, 6).annotate(
            cadastrador=Count('usuario')).order_by('-cadastrador', '-usuario__estado_processo', 'mais_antigo')

        entes_nao_analisados = self.annotate_componente_mais_antigo_por_situacao(entes, 1).annotate(
            cadastrador=Count('usuario')).order_by('-cadastrador', '-usuario__estado_processo', 'mais_antigo')

        entes = entes_nao_analisados | entes_diligencia | entes_concluidos

        return entes


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
        municipio = Municipio.objects.get(usuario__id=context['usuario'].id)

        if municipio.cidade:
            context['historico_sistemas'] = SistemaCultura.objects.por_municipio(municipio.estado, municipio.cidade)
        else:
            context['historico_sistemas'] = SistemaCultura.objects.por_municipio(municipio.estado)

        try:

            if situacao == '3':
                historico = Historico.objects.filter(usuario_id=context['usuario'].id)
                historico = historico[0]
                context['dado_situacao'] = historico.descricao

            elif situacao == '2':
                context['dado_situacao'] = municipio.localizacao

            elif situacao == '4':
                context['dado_situacao'] = municipio.numero_processo

            elif situacao == '6':
                context['dado_situacao'] = context['usuario'].data_publicacao_acordo.strftime('%d/%m/%Y')
                context['link_publicacao'] = context['usuario'].link_publicacao_acordo
        except:
            pass
        return context


class DetalharEnte(DetailView):
    model = SistemaCultura
    template_name = 'detalhe_municipio.html'

    def get_context_data(self, **kwargs):
        context = super(DetalharEnte, self).get_context_data(**kwargs)
        sistema_cultura = context['sistemacultura']

        if sistema_cultura.cidade:
            context['historico_sistemas'] = SistemaCultura.objects.por_municipio(municipio.estado, municipio.cidade)
        else:
            context['historico_sistemas'] = SistemaCultura.objects.por_municipio(municipio.estado)

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


class ListarDocumentosComponentes(ListView):
    paginate_by = 10

    def get_template_names(self):
        return ['gestao/inserir_documentos/%s.html' % self.kwargs['template']]

    def get_queryset(self):
        q = self.request.GET.get('q', None)

        usuarios = Usuario.objects.filter(estado_processo='6')

        if q:
            usuarios = usuarios.filter(
                municipio__cidade__nome_municipio__icontains=q)

        return usuarios


class InserirSistema(CreateView):
    template_name = 'gestao/inserir_documentos/inserir_sistema.html'
    form_class = CriarSistemaForm

    def get_form_kwargs(self):
        kwargs = super(InserirSistema, self).get_form_kwargs()
        pk = self.kwargs['pk']
        kwargs['plano'] = PlanoTrabalho.objects.get(pk=pk)
        return kwargs

    def get_success_url(self):
        return reverse_lazy('gestao:listar_documentos', kwargs={'template': 'listar_sistemas'})


class AlterarSistema(UpdateView):
    template_name = 'gestao/inserir_documentos/inserir_sistema.html'
    form_class = AlterarSistemaForm
    model = CriacaoSistema

    def get_success_url(self):
        return reverse_lazy('gestao:listar_documentos', kwargs={'template': 'listar_sistemas'})


class InserirOrgao(CreateView):
    template_name = 'gestao/inserir_documentos/inserir_orgao.html'
    form_class = CriarOrgaoForm

    def get_form_kwargs(self):
        kwargs = super(InserirOrgao, self).get_form_kwargs()
        pk = self.kwargs['pk']
        kwargs['plano'] = PlanoTrabalho.objects.get(pk=pk)
        return kwargs

    def get_success_url(self):
        return reverse_lazy('gestao:listar_documentos', kwargs={'template': 'listar_orgaos'})


class AlterarOrgao(UpdateView):
    template_name = 'gestao/inserir_documentos/inserir_orgao.html'
    form_class = AlterarOrgaoForm
    model = OrgaoGestor

    def get_success_url(self):
        return reverse_lazy('gestao:listar_documentos', kwargs={'template': 'listar_orgaos'})


class InserirConselho(CreateView):
    template_name = 'gestao/inserir_documentos/inserir_conselho.html'
    form_class = CriarConselhoForm

    def get_form_kwargs(self):
        kwargs = super(InserirConselho, self).get_form_kwargs()
        pk = self.kwargs['pk']
        kwargs['plano'] = PlanoTrabalho.objects.get(pk=pk)
        return kwargs

    def get_success_url(self):
        return reverse_lazy('gestao:listar_documentos', kwargs={'template': 'listar_conselhos'})


class AlterarConselho(UpdateView):
    template_name = 'gestao/inserir_documentos/inserir_conselho.html'
    form_class = AlterarConselhoForm
    model = ConselhoCultural

    def get_success_url(self):
        return reverse_lazy('gestao:listar_documentos', kwargs={'template': 'listar_conselhos'})


class InserirFundo(CreateView):
    template_name = 'gestao/inserir_documentos/inserir_fundo.html'
    form_class = CriarFundoForm

    def get_form_kwargs(self):
        kwargs = super(InserirFundo, self).get_form_kwargs()
        pk = self.kwargs['pk']
        kwargs['plano'] = PlanoTrabalho.objects.get(pk=pk)
        return kwargs

    def get_success_url(self):
        return reverse_lazy('gestao:listar_documentos', kwargs={'template': 'listar_fundos'})


class AlterarFundo(UpdateView):
    template_name = 'gestao/inserir_documentos/inserir_fundo.html'
    form_class = AlterarFundoForm
    model = FundoCultura

    def get_success_url(self):
        return reverse_lazy('gestao:listar_documentos', kwargs={'template': 'listar_fundos'})
    

class InserirPlano(CreateView):
    template_name = 'gestao/inserir_documentos/inserir_plano.html'
    form_class = CriarPlanoForm

    def get_form_kwargs(self):
        kwargs = super(InserirPlano, self).get_form_kwargs()
        pk = self.kwargs['pk']
        kwargs['plano'] = PlanoTrabalho.objects.get(pk=pk)
        return kwargs

    def get_success_url(self):
        return reverse_lazy('gestao:listar_documentos', kwargs={'template': 'listar_planos'})


class AlterarPlano(UpdateView):
    template_name = 'gestao/inserir_documentos/inserir_plano.html'
    form_class = AlterarPlanoForm
    model = PlanoCultura

    def get_success_url(self):
        return reverse_lazy('gestao:listar_documentos', kwargs={'template': 'listar_planos'})


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


class DiligenciaComponenteView(CreateView):
    template_name = 'diligencia.html'
    model = DiligenciaSimples
    form_class = DiligenciaComponenteForm
    context_object_name = "diligencia"

    def get_form_kwargs(self):
        kwargs = super(DiligenciaComponenteView, self).get_form_kwargs()
        kwargs['componente'] = self.kwargs['componente']
        kwargs['sistema_cultura'] = self.get_sistema_cultura()
        kwargs['usuario'] = self.request.user.usuario

        return kwargs

    def get_success_url(self):
        sistema_cultura = self.get_sistema_cultura()
        return reverse_lazy('gestao:detalhar', kwargs={'pk': sistema_cultura.id})

    def get_sistema_cultura(self):
        return get_object_or_404(SistemaCultura, pk=int(self.kwargs['pk']))

    def get_componente(self):
        """ Retonar o componente baseado no argumento passado pela url"""
        sistema_cultura = self.get_sistema_cultura()
        componente = None

        try:
            componente = getattr(sistema_cultura,
                                       self.kwargs['componente'])
            assert componente
        except(AssertionError, AttributeError):
            raise Http404('Componente não existe')

        return componente

    def get_context_data(self, form=None, **kwargs):
        context = super().get_context_data(**kwargs)
        componente = self.get_componente()
        ente_federado = self.get_sistema_cultura().ente_federado.nome

        context['arquivo'] = componente.arquivo
        context['ente_federado'] = self.get_sistema_cultura().ente_federado.nome
        context['sistema_cultura'] = self.get_sistema_cultura().id
        context['data_envio'] = "--/--/----"
        context['componente'] = componente

        return context

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form), status=400)


class DiligenciaGeralCreateView(CreateView, TemplatedEmailFormViewMixin):
    template_name = 'diligencia.html'
    model = DiligenciaSimples
    form_class = DiligenciaGeralForm

    templated_email_template_name = "diligencia"
    templated_email_from_email = "naoresponda@cultura.gov.br"

    def get_form_kwargs(self):
        kwargs = super(DiligenciaGeralCreateView, self).get_form_kwargs()
        kwargs['sistema_cultura'] = self.get_sistema_cultura()
        kwargs['usuario'] = self.request.user.usuario

        return kwargs

    def get_context_data(self, form=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sistema_cultura'] = self.get_sistema_cultura().id
        context['situacoes'] = self.get_sistema_cultura().get_situacao_componentes()
        context['historico_diligencias'] = self.get_historico_diligencias()

        return context

    def get_historico_diligencias(self):
        historico_diligencias = SistemaCultura.historico.ente(
            cod_ibge=self.get_sistema_cultura().ente_federado.cod_ibge)

        return historico_diligencias

    def get_sistema_cultura(self):
        return get_object_or_404(SistemaCultura, pk=int(self.kwargs['pk']))

    def templated_email_get_recipients(self, form):
        return self.get_sistema_cultura().cadastrador.user.email

    def get_success_url(self):
        return reverse_lazy("gestao:detalhar", kwargs={"pk": self.get_sistema_cultura().id})


class DiligenciaGeralDetailView(DetailView):
    model = SistemaCultura
    fields = ['diligencia_simples']
    template_name = 'diligencia.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['sistema_cultura'] = self.object.id
        context['situacoes'] = self.object.get_situacao_componentes()
        return context


class SituacaoArquivoComponenteUpdateView(UpdateView):
    model = Componente
    fields = ['situacao']