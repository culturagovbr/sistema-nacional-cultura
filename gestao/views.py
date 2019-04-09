import json
import re

from django_datatables_view.base_datatable_view import BaseDatatableView
from django.utils.html import escape
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Q
from django.utils.translation import gettext as _
from django.http import QueryDict

from django.shortcuts import redirect
from django.shortcuts import render
from django.shortcuts import get_object_or_404

from django.http import Http404
from django.http import JsonResponse
from django.http import HttpResponse

from django.contrib.auth.models import User
from django.contrib import messages

from django.views.generic.detail import SingleObjectMixin

from django.views.generic import CreateView
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic import TemplateView

from django.views.generic.edit import UpdateView

from django.urls import reverse_lazy

from dal import autocomplete

from templated_email.generic_views import TemplatedEmailFormViewMixin

from adesao.models import Usuario
from adesao.models import Municipio
from adesao.models import SistemaCultura
from adesao.models import EnteFederado
from adesao.models import Gestor
from adesao.models import Funcionario
from adesao.models import LISTA_ESTADOS_PROCESSO

from planotrabalho.models import Componente
from planotrabalho.models import FundoDeCultura

from gestao.utils import empty_to_none, get_uf_by_mun_cod

from .models import DiligenciaSimples

from .forms import DiligenciaComponenteForm
from .forms import DiligenciaGeralForm
from .forms import AlterarDocumentosEnteFederadoForm
from .forms import AlterarUsuarioForm
from .forms import AlterarComponenteForm
from .forms import AlterarDadosEnte

from planotrabalho.forms import CriarComponenteForm
from planotrabalho.forms import CriarFundoForm

from .forms import CadastradorEnte

from adesao.views import AlterarSistemaCultura
from adesao.views import AlterarFuncionario
from adesao.views import CadastrarFuncionario


def dashboard(request, **kwargs):
    return render(request, "dashboard.html")


def plano_trabalho(request, **kwargs):

    return render(request, "plano_trabalho.html")


def listar_componentes(request, **kwargs):

    return render(request, "listar_componentes.html")


def ajax_consulta_entes(request):

    if not request.is_ajax():
        return JsonResponse(
            data={"message": "Esta não é uma requisição AJAX"}, status=400)

    queryset = SistemaCultura.sistema.filter(
            ente_federado__isnull=False).filter(
                Q(ente_federado__latitude__isnull=False) &
                Q(ente_federado__longitude__isnull=False)
        ).values(
            'id',
            'estado_processo',
            'ente_federado__nome',
            'ente_federado__cod_ibge',
            'ente_federado__longitude',
            'ente_federado__latitude',
        )

    sistemaList = [{
        'id': ente['id'],
        'estado_processo': ente['estado_processo'],
        'nome': ente['ente_federado__nome'],
        'sigla': get_uf_by_mun_cod(ente['ente_federado__cod_ibge']),
        'cod_ibge': ente['ente_federado__cod_ibge'],
        'latitude': ente['ente_federado__latitude'],
        'longitude': ente['ente_federado__longitude'],
        } for ente in queryset]

    entes = json.dumps(sistemaList, cls=DjangoJSONEncoder)
    return HttpResponse(entes, content_type='application/json')


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


def ajax_consulta_cpf(request):

    if not request.is_ajax():
        return JsonResponse(
            data={"message": "Esta não é uma requisição AJAX"},
            status=400)

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


class AcompanharPrazo(TemplateView):
    template_name = 'gestao/acompanhar_prazo.html'


def aditivar_prazo(request):
    if request.method == "POST":
        id = request.POST.get('id', None)
        sistema = SistemaCultura.objects.get(id=id)
        sistema.prazo = sistema.prazo + 2
        sistema.save()

    return JsonResponse(data={}, status=200)


class AcompanharSistemaCultura(TemplateView):
    template_name = 'gestao/adesao/acompanhar.html'


class AcompanharComponente(TemplateView):
    template_name = 'gestao/planotrabalho/acompanhar.html'
    # def get_template_names(self):
    #     return ['gestao/planotrabalho/acompanhar_legislacao.html' % self.kwargs['componente']]


# class AcompanharComponente(ListView):
#     paginate_by = 10

#     def get_template_names(self):
#         return ['gestao/planotrabalho/acompanhar_%s.html' % self.kwargs['componente']]

#     def get_queryset(self):
#         anexo = self.request.GET.get('anexo', None)
#         q = self.request.GET.get('q', None)
#         sistemas = SistemaCultura.sistema.filter(estado_processo='6')
#         kwargs = {'{0}'.format(self.kwargs['componente']): None}
#         sistemas = sistemas.exclude(**kwargs)

#         if anexo == 'arquivo':
#             kwargs = {'{0}__situacao'.format(self.kwargs['componente']): 1}
#             sistemas = sistemas.filter(**kwargs)
#             kwargs = {'{0}__arquivo'.format(self.kwargs['componente']): None}
#             sistemas = sistemas.exclude(**kwargs)
#         else:
#             raise Http404

#         if q:
#             sistemas = sistemas.filter(
#                 ente_federado__nome__unaccent__icontains=q)

#         return sistemas


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
        historico = SistemaCultura.historico.filter(ente_federado=ente_federado)
        context['historico'] = historico.distinct('cadastrador').order_by('cadastrador')[:10]

        return context


class AlterarDadosSistemaCultura(AlterarSistemaCultura):
    template_name = "alterar_ente.html"

    def get_success_url(self):
        sistema = SistemaCultura.objects.get(id=self.kwargs['pk'])
        return reverse_lazy(
            'gestao:detalhar',
            kwargs={'cod_ibge': sistema.ente_federado.cod_ibge})


class AlterarFuncionario(AlterarFuncionario):
    template_name = "criar_funcionario.html"

    def get_success_url(self):
        funcionario = Funcionario.objects.get(id=self.kwargs['pk'])
        sistema = getattr(funcionario, 'sistema_cultura_%s' % self.kwargs['tipo'])
        return reverse_lazy(
            'gestao:detalhar',
            kwargs={'cod_ibge': sistema.all()[0].ente_federado.cod_ibge})


class CadastrarFuncionario(CadastrarFuncionario):
    template_name = "criar_funcionario.html"

    def get_success_url(self):
        sistema = SistemaCultura.objects.get(id=self.kwargs['sistema'])
        return reverse_lazy(
            'gestao:detalhar',
            kwargs={'cod_ibge': sistema.ente_federado.cod_ibge})


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


class ListarUsuarios(TemplateView):
    template_name = 'gestao/listar_usuarios.html'


class AlterarUsuario(UpdateView):
    model = User
    form_class = AlterarUsuarioForm
    template_name = 'gestao/listar_usuarios.html'
    success_url = reverse_lazy('gestao:usuarios')

    def get_success_url(self):
        messages.success(
            self.request,
            'Situação de CPF: ' + str(self.object) + ' alterada com sucesso.')
        return reverse_lazy('gestao:usuarios')


def alterar_usuario(request):
    field_name = request.POST.get('name', None)
    field_value = request.POST.get('value', None)
    id = request.POST.get('pk', None)

    try:
        kwargs = QueryDict(mutable=True)
        kwargs[field_name] = field_value

        form = AlterarUsuarioForm(kwargs)
        if form.is_valid():
            user = User.objects.get(id=id)
            setattr(user, field_name, field_value)
            user.save()
            return JsonResponse(data={"data": {
                "code": 200,
                "id": id,
                field_name: field_value,
                "message": "Alterado com sucesso!"
            }}, status=200)
    except Exception:
        return JsonResponse(data={
            "error": {
                "code": 500,
                "message": "Ocorreu algum problema ao editar o usuário.",
                "errors": [{"message": "Ocorreu algum problema ao editar o usuário."}]
            }
        }, status=500)


class ListarDocumentosEnteFederado(ListView):
    template_name = 'gestao/inserir_documentos/inserir_entefederado.html'
    paginate_by = 10

    def get_queryset(self):
        ente_federado = self.request.GET.get('ente_federado', None)

        sistema = SistemaCultura.sistema.filter(estado_processo__range=('1', '5'))

        if ente_federado:
            sistema = sistema.filter(
                ente_federado__nome__unaccent__icontains=ente_federado)

        return sistema


class AlterarDocumentosEnteFederado(UpdateView):

    template_name = 'gestao/inserir_documentos/alterar_entefederado.html'
    form_class = AlterarDocumentosEnteFederadoForm
    model = Gestor

    def get_success_url(self):
        messages.success(self.request, 'Ente Federado alterado com sucesso')
        return reverse_lazy('gestao:inserir_entefederado')


class ListarDocumentosComponentes(TemplateView):

    def get_template_names(self):
        return ['gestao/inserir_documentos/%s.html' % self.kwargs['template']]


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
    template_name = 'gestao/inserir_documentacao.html'

    def get_success_url(self):
        messages.success(self.request, 'Sistema da Cultura alterado com sucesso')
        return reverse_lazy(
            'gestao:listar_documentos',
            kwargs={'template': 'listar_%s' % self.kwargs['componente']})


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
        return reverse_lazy(
            'gestao:listar_documentos',
            kwargs={'template': 'listar_fundo_cultura'})


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
            componente = getattr(
                sistema_cultura,
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
        context['historico_diligencias_componentes'] = \
            self.get_sistema_cultura().get_componentes_diligencias()

        return context

    def get_historico_diligencias(self):
        historico_diligencias = DiligenciaSimples.objects.filter(
            sistema_cultura__ente_federado__cod_ibge=self.get_sistema_cultura()
            .ente_federado.cod_ibge)

        return historico_diligencias

    def get_sistema_cultura(self):
        return get_object_or_404(SistemaCultura, pk=int(self.kwargs['pk']))

    def templated_email_get_recipients(self, form):
        recipiente_list = [self.get_sistema_cultura().cadastrador.user.email]

        return recipiente_list

    def get_success_url(self):
        return reverse_lazy("gestao:detalhar", kwargs={
            "cod_ibge": self.get_sistema_cultura().ente_federado.cod_ibge})


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


class DataTableEntes(BaseDatatableView):
    max_display_length = 150

    def get_initial_queryset(self):
        sistema = SistemaCultura.objects.distinct('ente_federado__cod_ibge').order_by(
            'ente_federado__cod_ibge').filter(
                ente_federado__isnull=False
            ).values_list('id', flat=True)

        return SistemaCultura.objects.filter(id__in=sistema)

    def filter_queryset(self, qs):
        search = self.request.POST.get('search[value]', None)

        if search:
            query = Q()
            filtros_queryset = [
                Q(ente_federado__nome__unaccent__icontains=search),
                Q(gestor__nome__unaccent__icontains=search),
                Q(gestor__rg__contains=search),
                Q(gestor__cpf__contains=search),
                Q(sede__cnpj__contains=search)
            ]
            estados_para_pesquisa = []
            for tupla_estado_processo in LISTA_ESTADOS_PROCESSO:

                contem_pesquisa = \
                    True if search.lower() in tupla_estado_processo[1].lower() \
                    else False
                if contem_pesquisa:
                    estados_para_pesquisa.append(
                        Q(estado_processo=tupla_estado_processo[0])
                    )

            filtros_queryset.extend(estados_para_pesquisa)

            for filtro in filtros_queryset:
                query |= filtro

            qs = qs.filter(query)

        return qs

    def prepare_results(self, qs):
        json_data = []

        for item in qs:
            json_data.append([
                escape(item.id),
                escape(item.ente_federado),
                escape(item.gestor.nome) if item.gestor else '',
                escape(item.gestor.rg) if item.gestor else '',
                escape(item.gestor.cpf) if item.gestor else '',
                escape(item.sede.cnpj) if item.sede else '',
                escape(item.get_estado_processo_display()),
                escape(item.ente_federado.cod_ibge) if item.ente_federado else '',
                escape(item.data_criacao),
                escape(
                    item.gestor.termo_posse.url if item.gestor and item.gestor.termo_posse else ''
                ),
                escape(
                    item.gestor.rg_copia.url if item.gestor and item.gestor.rg_copia else ''
                ),
                escape(
                    item.gestor.cpf_copia.url if item.gestor and item.gestor.cpf_copia else ''
                ),
            ])
        return json_data


class DataTablePrazo(BaseDatatableView):
    def get_initial_queryset(self):
        sistema = SistemaCultura.sistema.values_list('id', flat=True)

        return SistemaCultura.objects.filter(id__in=sistema).filter(
            estado_processo='6',
            data_publicacao_acordo__isnull=False)

    def filter_queryset(self, qs):
        search = self.request.POST.get('search[value]', None)

        if search:
            where = \
                Q(ente_federado__nome__unaccent__icontains=search) | \
                Q(sede__cnpj__contains=search)
            if search.isdigit():
                where |= Q(prazo=search)

            return qs.filter(where)

        return qs

    def prepare_results(self, qs):
        json_data = []
        for item in qs:
            json_data.append([
                item.id,
                escape(item.ente_federado),
                escape(item.sede.cnpj) if item.sede else '',
                item.data_publicacao_acordo.strftime(
                    "%d de %B de %Y") if item.data_publicacao_acordo else '',
                escape(item.prazo),
            ])
        return json_data


class DataTableUsuarios(BaseDatatableView):
    def get_initial_queryset(self):
        return Usuario.objects.all()

    def filter_queryset(self, qs):
        search = self.request.POST.get('search[value]', None)

        if search:
            query = Q()
            search_bool_field = {}
            search_lower = search.lower()

            search_bool_field['is_staff'] = True if search_lower in 'administrador' else False \
                if search_lower in 'cadastrador' else ''
            search_bool_field['is_active'] = True if search_lower in 'ativo' else False \
                if search_lower in 'inativo' else ''

            filtros_queryset = [
                Q(user__username__icontains=search),
                Q(nome_usuario__icontains=search),
                Q(user__email__icontains=search)
            ]

            for key, value in search_bool_field.items():
                if type(value) != bool:
                    continue
                q = Q(**{"user__%s" % key: value})
                filtros_queryset.append(q)

            for filtro in filtros_queryset:
                query |= filtro

            qs = qs.filter(query)

        return qs

    def prepare_results(self, qs):
        json_data = []
        for item in qs:
            try:
                sistema = SistemaCultura.sistema.get(
                    cadastrador=item.id)
                ente_nome = sistema.ente_federado.nome
                ente_id = sistema.ente_federado.cod_ibge
            except SistemaCultura.DoesNotExist:
                ente_nome = ''
                ente_id = ''
                pass

            json_data.append([
                item.user.id,
                item.user.username,
                item.nome_usuario,
                item.user.email,
                item.user.last_login if item.user.last_login else '',
                'Ativo' if item.user.is_active else 'Inativo',
                'Administrador' if item.user.is_staff else 'Cadastrador',
                ente_nome,
                ente_id,
                item.user.date_joined,
            ])
        return json_data


class DataTablePlanoTrabalho(BaseDatatableView):
    def get_initial_queryset(self):
        sistemas = SistemaCultura.sistema.values_list('id', flat=True)
        sistemas = SistemaCultura.objects.filter(id__in=sistemas, estado_processo='6')
        componente = self.request.POST.get('componente', None)

        sistemas = sistemas.filter(estado_processo='6')
        kwargs = {'{0}'.format(componente): None}
        sistemas = sistemas.exclude(**kwargs)

        kwargs = {'{0}__situacao'.format(componente): 1}
        sistemas = sistemas.filter(**kwargs)
        kwargs = {'{0}__arquivo'.format(componente): None}
        sistemas = sistemas.exclude(**kwargs)

        return sistemas

    def filter_queryset(self, qs):
        search = self.request.POST.get('search[value]', None)

        if search:
            return qs.filter(Q(ente_federado__nome__unaccent__icontains=search) |
                Q(sede__cnpj__contains=search))

        return qs

    def prepare_results(self, qs):
        json_data = []
        componente = self.request.POST.get('componente', None)
        for item in qs:
            json_data.append([
                item.id,
                item.ente_federado.__str__(),
                escape(item.sede.cnpj) if item.sede else '',
                getattr(item, componente).arquivo.url,
                componente,
            ])
        return json_data


class DataTableListarDocumentos(BaseDatatableView):
    def get_initial_queryset(self):
        sistema = SistemaCultura.sistema.values_list('id', flat=True)
        qs = SistemaCultura.objects.filter(id__in=sistema).filter(
            estado_processo='6')

        return qs

    def filter_queryset(self, qs):
        search = self.request.POST.get('search[value]', None)

        if search:
            return qs.filter(
                Q(ente_federado__nome__unaccent__icontains=search) |
                Q(sede__cnpj__contains=search))

        return qs

    def prepare_results(self, qs):
        json_data = []
        for item in qs:
            json_data.append([
                item.id,
                escape(item.ente_federado),
                escape(item.sede.cnpj) if item.sede else '',
                item.legislacao.arquivo.url if item.legislacao and item.legislacao.arquivo else '',
            ])
        return json_data