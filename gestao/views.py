from django.db.models import Case, When, DateField, Count, Q
from django.db.models.functions import Least
from django.utils.translation import gettext as _

from django.shortcuts import redirect
from django.shortcuts import render
from django.shortcuts import get_object_or_404

from django.http import Http404
from django.http import JsonResponse

from django.contrib.auth.models import User
from django.contrib import messages

from django.views.generic.detail import SingleObjectMixin

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
from adesao.models import EnteFederado

from planotrabalho.models import PlanoTrabalho
from planotrabalho.models import CriacaoSistema
from planotrabalho.models import PlanoCultura
from planotrabalho.models import FundoCultura
from planotrabalho.models import OrgaoGestor
from planotrabalho.models import ConselhoCultural
from planotrabalho.models import SituacoesArquivoPlano
from planotrabalho.models import Componente
from planotrabalho.models import FundoDeCultura

from gestao.utils import empty_to_none

from adesao.models import Uf

from .models import DiligenciaSimples

from .forms import DiligenciaComponenteForm, DiligenciaGeralForm, AlterarDocumentosEnteFederadoForm

from .forms import AlterarCadastradorForm
from .forms import AlterarUsuarioForm
from .forms import AlterarComponenteForm
from .forms import AlterarDadosEnte

from planotrabalho.forms import CriarComponenteForm
from planotrabalho.forms import CriarFundoForm

from .forms import CadastradorEnte

from itertools import chain
import datetime


# Acompanhamento das adesões
class AlterarCadastrador(UpdateView):
    """AlterarCadastrador
    Altera o cadastrador de um Municipio aderido
    """
    queryset = SistemaCultura.sistema.all()
    template_name = 'cadastrador.html'
    form_class = AlterarCadastradorForm

    def get_form_kwargs(self):
        kwargs = super(AlterarCadastrador, self).get_form_kwargs()
        self.cod_ibge = self.kwargs['cod_ibge']
        kwargs.update(self.kwargs)
        return kwargs

    def get_success_url(self):
       return reverse_lazy('gestao:alterar_cadastrador', kwargs={'cod_ibge': self.cod_ibge})

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Cadastrador alterado com sucesso')
        return super(AlterarCadastrador, self).form_valid(form)


class CidadeChain(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        """ Filtra todas as cidade de uma determinada UF """

        uf_pk = self.forwarded.get('estado', None)

        if uf_pk:
            choices = Cidade.objects\
                .filter(Q(uf__pk=uf_pk) & Q(nome_municipio__unaccent__icontains=self.q))\
                .values_list('pk', 'nome_municipio', named=True)
        else:
            choices = Cidade.objects\
                .filter(uf__sigla__iexact=self.q)\
                .values_list('pk', 'nome_municipio', named=True)
        return choices


class EnteChain(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        """ Filtra todas as cidade de uma determinada UF """
        choices = EnteFederado.objects.filter(Q(nome__unaccent__icontains=self.q))

        return choices

    def get_ente_name(self, item):
        if item.cod_ibge > 100:
            nome = item.__str__()
        else:
            nome = "Estado de " + item.nome

        return nome

    def get_result_label(self, item):
        return self.get_ente_name(item)

    def get_selected_result_label(self, item):
        return self.get_ente_name(item)


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


def ajax_consulta_cpf(request):

    if not request.is_ajax():
        return JsonResponse(data={"message": "Esta não é uma requisição AJAX"}, status=400)

    cpf = request.POST.get('cpf', None)
    if not cpf:
        return JsonResponse(data={"message": "CPF não informado"}, status=400)

    try:
        nome = Usuario.objects.get(user__username=cpf).nome_usuario
    except Usuario.DoesNotExist:
        return JsonResponse(data={"message": "CPF não encontrado"}, status=404)

    return JsonResponse(data={"data": {"nome": nome}})


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
                municipio__cidade__nome_municipio__unaccent__icontains=ente_federado).order_by('municipio__estado__nome_uf')
            estado = Usuario.objects.filter(
                municipio__cidade__isnull=True,
                municipio__estado__nome_uf__unaccent__icontains=ente_federado).order_by('municipio__estado__nome_uf')

            return municipio | estado
        return Usuario.objects.filter(estado_processo='6', data_publicacao_acordo__isnull=False).order_by(
            'municipio__estado__nome_uf', 'municipio__cidade__nome_municipio')


def aditivar_prazo(request, id,page):
    if request.method == "POST":
        user = Usuario.objects.get(id=id)
        print(page)
        user.prazo = user.prazo + 2
        user.save()

        if user.municipio.cidade:
            ente = user.municipio.cidade.nome_municipio
        else:
            ente = user.municipio.estado.nome_uf

        message = 'Prazo de ' + ente + ' alterado para '+ str(user.prazo) + ' anos com sucesso'
        messages.success(request, message)


    return redirect(reverse_lazy('gestao:acompanhar_prazo') + '?page=' + page)


class AcompanharSistemaCultura(ListView):
    model = SistemaCultura
    template_name = 'gestao/adesao/acompanhar.html'
    paginate_by = 10

    def remove_repeticoes(self, lista):
        ja_adicionados = set()
        lista_sem_repeticoes = []
        for sistema in lista:
                if sistema not in ja_adicionados:
                    lista_sem_repeticoes.append(sistema)
                    ja_adicionados.add(sistema)

        return lista_sem_repeticoes

    def annotate_componente_mais_antigo_por_situacao(self, componentes, *args):
        componentes = componentes.annotate(
            data_legislacao_sem_analise=Case(
                When(legislacao__situacao__in=args, then='legislacao__data_envio'),
                default=None,
                output_field=DateField(),
            ),
             data_orgao_sem_analise=Case(
                When(orgao_gestor__situacao__in=args, then='orgao_gestor__data_envio'),
                default=None,
                output_field=DateField(),
            ),
             data_conselho_sem_analise=Case(
                When(conselho__situacao__in=args, then='conselho__data_envio'),
                default=None,
                output_field=DateField(),
            ),
             data_plano_sem_analise=Case(
                When(plano__situacao__in=args, then='plano__data_envio'),
                default=None,
                output_field=DateField(),
            ),
            data_fundo_sem_analise=Case(
                When(fundo_cultura__situacao__in=args, then='fundo_cultura__data_envio'),
                default=None,
                output_field=DateField(),
            )
        ).annotate(
            mais_antigo=Least('data_legislacao_sem_analise', 'data_orgao_sem_analise', 'data_conselho_sem_analise', 'data_plano_sem_analise',
                'data_fundo_sem_analise')
        )

        return componentes

    def get_queryset(self):
        situacao = self.request.GET.get('situacao', None)
        ente_federado = self.request.GET.get('ente_federado', None)

        if situacao in ('0', '1', '2', '3', '4', '5', '6'):
            sistemas = SistemaCultura.objects.filter(estado_processo=situacao)

        if ente_federado:
            sistemas = SistemaCultura.objects.filter(
                ente_federado__nome__unaccent__icontains=ente_federado)
        else:
            sistemas = SistemaCultura.objects.all()

        sistemas_entes_distintos = sistemas.distinct('ente_federado')

        sistemas_concluidos = self.annotate_componente_mais_antigo_por_situacao(sistemas, 2, 3).filter(
            estado_processo='6').exclude(mais_antigo=None).order_by('mais_antigo').filter(id__in=sistemas_entes_distintos)

        sistemas_diligencia = self.annotate_componente_mais_antigo_por_situacao(sistemas, 4, 5, 6).filter(
            estado_processo='6').exclude(mais_antigo=None).order_by('mais_antigo').filter(id__in=sistemas_entes_distintos)

        sistemas_nao_enviados = self.annotate_componente_mais_antigo_por_situacao(sistemas, 0).filter(
            estado_processo='6').exclude(mais_antigo=None).order_by('mais_antigo').filter(id__in=sistemas_entes_distintos)

        sistemas_nao_analisados = self.annotate_componente_mais_antigo_por_situacao(sistemas, 1).filter(
            estado_processo='6').exclude(mais_antigo=None).order_by('mais_antigo').filter(id__in=sistemas_entes_distintos)

        sistemas_publicados_sem_componentes = sistemas.filter(Q(estado_processo='6') &
            Q(legislacao=None) &
            Q(orgao_gestor=None) &
            Q(conselho=None) &
            Q(plano=None) &
            Q(fundo_cultura=None)).filter(
            id__in=sistemas_entes_distintos)

        sistemas = sistemas.exclude(estado_processo='6').annotate(
            tem_cadastrador=Count('cadastrador')).order_by('-tem_cadastrador', '-estado_processo').filter(
            id__in=sistemas_entes_distintos)
 
        sistemas = list(chain(sistemas_nao_analisados, sistemas_diligencia, 
            sistemas_nao_enviados, sistemas_concluidos, sistemas_publicados_sem_componentes, sistemas))
        sistemas = self.remove_repeticoes(sistemas)

        return sistemas


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


class AcompanharComponente(ListView):
    paginate_by = 10

    def get_template_names(self):
        return ['gestao/planotrabalho/acompanhar_%s.html' % self.kwargs['componente']]

    def get_queryset(self):
        anexo = self.request.GET.get('anexo', None)
        q = self.request.GET.get('q', None)
        sistemas = SistemaCultura.sistema.filter(estado_processo='6')
        kwargs = {'{0}'.format(self.kwargs['componente']): None}
        sistemas = sistemas.exclude(**kwargs)

        if anexo == 'arquivo':
            kwargs = {'{0}__situacao'.format(self.kwargs['componente']): 1}
            sistemas = sistemas.filter(**kwargs)
            kwargs = {'{0}__arquivo'.format(self.kwargs['componente']): None}
            sistemas = sistemas.exclude(**kwargs)
        else:
            raise Http404

        if q:
            sistemas = sistemas.filter(
                ente_federado__nome__unaccent__icontains=q)

        return sistemas


class LookUpAnotherFieldMixin(SingleObjectMixin):

    lookup_field = None

    def get_object(self, queryset=None):

        if queryset is None:
            queryset = self.get_queryset()

        pk = self.kwargs.get(self.pk_url_kwarg)
        slug = self.kwargs.get(self.slug_url_kwarg)
        lookup_field = self.lookup_field

        if pk is not None and lookup_field is None:
            queryset = queryset.filter(pk=pk)

        if slug is not None and (pk is None or self.query_pk_and_slug):
            slug_field = self.get_slug_field()
            queryset = queryset.filter(**{slug_field: slug})

        if lookup_field is not None:
            queryset = queryset.filter(**{lookup_field: pk})

        if pk is None and slug is None and lookup_field is None:
            raise AttributeError("Generic detail view %s must be called with "
                                 "either an object pk or a slug."
                                 % self.__class__.__name__)

        try:
            # Get the single item from the filtered queryset
            obj = queryset.get()
        except queryset.model.DoesNotExist:
            raise Http404(_("No %(verbose_name)s found matching the query") %
                          {'verbose_name': queryset.model._meta.verbose_name})
        return obj


class DetalharEnte(DetailView, LookUpAnotherFieldMixin):
    model = SistemaCultura
    context_object_name = "ente"
    template_name = "detalhe_municipio.html"
    pk_url_kwarg = "cod_ibge"
    lookup_field = "ente_federado__cod_ibge"
    queryset = SistemaCultura.sistema.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ente_federado = context['object'].ente_federado
        historico = SistemaCultura.historico.filter(ente_federado=ente_federado)[:10]
        context['historico'] = historico

        return context


class AlterarDadosEnte(UpdateView, LookUpAnotherFieldMixin):
    model = SistemaCultura
    form_class = AlterarDadosEnte
    context_object_name = "ente"
    template_name = "detalhe_municipio.html"
    pk_url_kwarg = "cod_ibge"
    lookup_field = "ente_federado__cod_ibge"
    queryset = SistemaCultura.sistema.all()


class AlterarCadastradorEnte(UpdateView, LookUpAnotherFieldMixin):
    model = SistemaCultura
    queryset = SistemaCultura.sistema.all()
    form_class = CadastradorEnte
    context_object_name = "ente"
    template_name = "detalhe_municipio.html"
    pk_url_kwarg = "cod_ibge"
    lookup_field = "ente_federado__cod_ibge"


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
        messages.success(self.request, 'Situação de CPF: '+ str(self.object) + ' alterada com sucesso.')
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
                cidade__nome_municipio__unaccent__icontains=ente_federado)
            estado = Municipio.objects.filter(
                cidade__nome_municipio__isnull=True,
                estado__nome_uf__unaccent__icontains=ente_federado)

            return municipio | estado

        return Municipio.objects.filter(usuario__estado_processo__range=('1', '5'))


class AlterarDocumentosEnteFederado(UpdateView):

    template_name = 'gestao/inserir_documentos/alterar_entefederado.html'
    form_class = AlterarDocumentosEnteFederadoForm
    model = Municipio

    def get_success_url(self):
        messages.success(self.request, 'Ente Federado alterado com sucesso')
        return reverse_lazy('gestao:inserir_entefederado')


class ListarDocumentosComponentes(ListView):
    paginate_by = 10

    def get_template_names(self):
        return ['gestao/inserir_documentos/%s.html' % self.kwargs['template']]

    def get_queryset(self):
        q = self.request.GET.get('q', None)

        sistemas = SistemaCultura.sistema.filter(estado_processo='6')

        if q:
            sistemas = sistemas.filter(
                ente_federado__nome__unaccent__icontains=q)

        return sistemas


class InserirComponente(CreateView):

    def get_template_names(self):
        return ['gestao/inserir_documentos/inserir_%s.html' % self.kwargs['componente']]

    def get_form_kwargs(self):
        kwargs = super(InserirComponente, self).get_form_kwargs()
        pk = self.kwargs['pk']
        kwargs['tipo'] = self.kwargs['componente']
        kwargs['sistema'] = SistemaCultura.sistema.get(pk=pk)
        return kwargs

    def get_form_class(self):
        if self.kwargs['componente'] == 'fundo_cultura':
            form_class = CriarFundoForm
        else:
            form_class = CriarComponenteForm

        return form_class

    def get_success_url(self):
        messages.success(self.request, 'Sistema da Cultura inserido com sucesso')
        return reverse_lazy('gestao:listar_documentos', kwargs={'template': 'listar_%s' % self.kwargs['componente']})


class AlterarComponente(UpdateView):
    form_class = AlterarComponenteForm
    model = Componente

    def get_template_names(self):
        return ['gestao/inserir_documentos/inserir_%s.html' % self.kwargs['componente']]

    def get_success_url(self):
        messages.success(self.request, 'Sistema da Cultura alterado com sucesso')
        return reverse_lazy('gestao:listar_documentos',kwargs={'template': 'listar_%s' % self.kwargs['componente']})


class AlterarFundoCultura(UpdateView):
    form_class = CriarFundoForm
    model = FundoDeCultura
    template_name = 'gestao/inserir_documentos/inserir_fundo_cultura.html'

    def get_form_kwargs(self):
        kwargs = super(AlterarFundoCultura, self).get_form_kwargs()
        sistema_id = self.object.fundo_cultura.last().id
        self.sistema = SistemaCultura.objects.get(id=sistema_id)
        kwargs['sistema'] = self.sistema
        kwargs['tipo'] = 'fundo_cultura'
        return kwargs

    def get_success_url(self):
        messages.success(self.request, 'Sistema da Cultura alterado com sucesso')
        return reverse_lazy('gestao:listar_documentos',kwargs={'template': 'listar_fundo_cultura'})


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
                municipio__cidade__nome_municipio__unaccent__icontains=q)
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
        return reverse_lazy('gestao:detalhar', kwargs={'cod_ibge': sistema_cultura.ente_federado.cod_ibge})

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
        context['ente_federado'] = ente_federado
        context['sistema_cultura'] = self.get_sistema_cultura()
        context['data_envio'] = "--/--/----"
        context['componente'] = componente

        return context

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form), status=400)


class DiligenciaGeralCreateView(TemplatedEmailFormViewMixin, CreateView):
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
        context['sistema_cultura'] = self.get_sistema_cultura()
        context['situacoes'] = self.get_sistema_cultura().get_situacao_componentes()
        context['historico_diligencias'] = self.get_historico_diligencias()
        context['historico_diligencias_componentes'] = self.get_sistema_cultura().get_componentes_diligencias()

        return context

    def get_historico_diligencias(self):
        historico_diligencias = DiligenciaSimples.objects.filter(
            sistema_cultura__ente_federado__cod_ibge=self.get_sistema_cultura().ente_federado.cod_ibge)

        return historico_diligencias

    def get_sistema_cultura(self):
        return get_object_or_404(SistemaCultura, pk=int(self.kwargs['pk']))

    def templated_email_get_recipients(self, form):
        recipiente_list = list(self.get_sistema_cultura().cadastrador.user.email)
        return recipiente_list

    def get_success_url(self):
        return reverse_lazy("gestao:detalhar", kwargs={"cod_ibge": self.get_sistema_cultura().ente_federado.cod_ibge})


class DiligenciaGeralDetailView(DetailView):
    model = SistemaCultura
    fields = ['diligencia']
    template_name = 'diligencia.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['sistema_cultura'] = self.object.id
        context['situacoes'] = self.object.get_situacao_componentes()
        return context


class SituacaoArquivoComponenteUpdateView(UpdateView):
    model = Componente
    fields = ['situacao']