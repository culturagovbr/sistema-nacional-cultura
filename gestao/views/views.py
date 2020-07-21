import json
from django_datatables_view.base_datatable_view import BaseDatatableView

from django.utils.html import escape
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Q
from django.utils.translation import gettext as _
from django.http import QueryDict

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

from adesao.models import Usuario,Municipio,SistemaCultura,EnteFederado,Gestor,Funcionario,LISTA_ESTADOS_PROCESSO,TrocaCadastrador, SolicitacaoDeAdesao

from planotrabalho.models import Componente
from planotrabalho.models import FundoDeCultura
from planotrabalho.models import PlanoDeCultura
from planotrabalho.models import ConselhoDeCultura
from planotrabalho.models import OrgaoGestor2
from planotrabalho.models import LISTA_TIPOS_COMPONENTES

from planotrabalho.views import AlterarPlanoCultura
from planotrabalho.views import AlterarOrgaoGestor
from planotrabalho.views import AlterarFundoCultura
from planotrabalho.views import AlterarConselhoCultura

from planotrabalho.forms import CriarFundoFormGestao

from gestao.utils import empty_to_none, get_uf_by_mun_cod, scdc_user_group_required
from django.utils.decorators import method_decorator

from django.contrib.auth.models import Group

from django.contrib.auth.decorators import user_passes_test

from gestao.models import DiligenciaSimples, Contato

from gestao.forms import DiligenciaComponenteForm
from gestao.forms import DiligenciaGeralForm
from gestao.forms import AlterarDocumentosEnteFederadoForm
from gestao.forms import AlterarUsuarioForm
from gestao.forms import AlterarComponenteForm
from gestao.forms import AlterarDadosEnte
from gestao.forms import CriarContatoForm

from planotrabalho.forms import CriarComponenteForm
from planotrabalho.forms import CriarFundoForm
from planotrabalho.forms import CriarConselhoForm
from planotrabalho.forms import CriarOrgaoGestorForm, CriarOrgaoGestorFormGestao
from planotrabalho.forms import CriarPlanoForm

from gestao.forms import CadastradorEnte
from gestao.forms import AditivarPrazoForm

from adesao.views import AlterarSistemaCultura
from adesao.views import AlterarFuncionario
from adesao.views import CadastrarFuncionario

from snc.client import Client

from django.core.files.storage import FileSystemStorage

from datetime import date


def dashboard(request, **kwargs):
    return render(request, "dashboard.html")


@user_passes_test(scdc_user_group_required)
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

    cod_ibge_df = 53
    sistema_cultura_df = SistemaCultura.sistema.get(
        ente_federado__cod_ibge=cod_ibge_df)
    sistemaList.append({
        'id': sistema_cultura_df.id,
        'estado_processo': sistema_cultura_df.estado_processo,
        'nome': sistema_cultura_df.ente_federado.nome,
        'sigla': get_uf_by_mun_cod(sistema_cultura_df.ente_federado.cod_ibge),
        'cod_ibge': sistema_cultura_df.ente_federado.cod_ibge,
        'latitude': sistema_cultura_df.ente_federado.latitude,
        'longitude': sistema_cultura_df.ente_federado.longitude,
    })

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = AditivarPrazoForm()
        return context


def aditivar_prazo(request):
    if request.method == "POST":
        id = request.POST.get('id', None)
        sistema = SistemaCultura.objects.get(id=id)

        form = AditivarPrazoForm(request.POST, request.FILES)
        field_name = 'oficio_prorrogacao_prazo'

        if form.is_valid():
            oficio_prorrogacao_prazo = request.FILES.get(
                field_name, None)
            fs = FileSystemStorage(location=f"./media/{field_name}/")
            filename = fs.save(oficio_prorrogacao_prazo.name, oficio_prorrogacao_prazo)
            sistema.prazo = sistema.prazo + 2
            sistema.oficio_prorrogacao_prazo = f"/oficio_prorrogacao_prazo/{filename}"
            sistema.save()
        else:
            return JsonResponse(data={}, status=422)
    return JsonResponse(data={}, status=200)


class AcompanharSistemaCultura(TemplateView):
    template_name = 'gestao/adesao/acompanhar.html'


class AcompanharComponente(TemplateView):
    template_name = 'gestao/planotrabalho/acompanhar.html'

class AcompanharTrocaCadastrador(TemplateView):
    template_name = 'gestao/troca-cadastrador/acompanhar.html'


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
        sistema = context['object']
        context['historico'] = sistema.historico_cadastradores()[:10]
        context['historico_contatos'] = sistema.contatos.all()
        if sistema.sede:
            context['informacao_cnpj'] = Client().consulta_cnpj(sistema.sede.cnpj)

        sistema = self.get_queryset().get(id=self.object.id)

        context['componentes_restantes'] = []
        componentes = {
            0: "legislacao",
            1: "orgao_gestor",
            2: "fundo_cultura",
            3: "conselho",
            4: "plano",
        }

        for componente_id, componente_nome in componentes.items():
            componente_sistema = getattr(sistema, componente_nome, None)
            arquivo_componente = getattr(componente_sistema, 'arquivo', None)
            descricao = ''
            if not arquivo_componente:
                descricao = self.get_descricao_componente(componente_id)
                if componente_nome == 'fundo_cultura':
                    descricao += ' (Lei e Comprovante do CNPJ)'

                if componente_nome == 'conselho':
                    descricao += ' (Lei e Ata)'

                context['componentes_restantes'].append({
                    'nome': componente_nome,
                    'descricao': descricao
                })

        context['form'] = CadastradorEnte()

        # Validação dos documentos concluidos
        has_legislacao_concluido = self.get_valida_arquivo_concluido(sistema.legislacao)
        has_plano_concluido = self.get_valida_arquivo_concluido(sistema.plano)
        has_conselho_concluido = self.get_valida_arquivo_concluido(sistema.conselho)
        has_fundo_cultura_concluido = self.get_valida_arquivo_concluido(
            sistema.fundo_cultura)
        has_orgao_gestor_concluido = self.get_valida_arquivo_concluido(
            sistema.orgao_gestor)
        has_conselho_lei_concluido = bool(
            sistema.conselho) and self.get_valida_arquivo_concluido(sistema.conselho.lei)
        has_comprovante_cnpj_concluido = bool(sistema.fundo_cultura) and self.get_valida_arquivo_concluido(
            sistema.fundo_cultura.comprovante_cnpj)

        has_legislacao_arquivo = self.get_valida_arquivo(sistema.legislacao)
        has_plano_arquivo = self.get_valida_arquivo(sistema.plano)
        has_conselho_arquivo = self.get_valida_arquivo(sistema.conselho)
        has_fundo_cultura_arquivo = self.get_valida_arquivo(sistema.fundo_cultura)
        has_orgao_gestor_arquivo = self.get_valida_arquivo(sistema.orgao_gestor)
        has_conselho_lei_arquivo = bool(
            sistema.conselho) and self.get_valida_arquivo(sistema.conselho.lei)
        has_comprovante_cnpj_arquivo = bool(sistema.fundo_cultura) and self.get_valida_arquivo(
            sistema.fundo_cultura.comprovante_cnpj)

        has_gestor_termo_posse = bool(sistema.gestor) and self.get_valida_documento_gestor(
            sistema.gestor.termo_posse)
        has_gestor_cpf_copia = bool(sistema.gestor) and self.get_valida_documento_gestor(
            sistema.gestor.cpf_copia)
        has_gestor_rg_copia = bool(sistema.gestor) and self.get_valida_documento_gestor(
            sistema.gestor.rg_copia)

        # Situações do Ente Federado
        context[
            'has_analise_nao_correcao'] = sistema.has_not_diligencias_enviadas_aprovadas() and has_legislacao_concluido and has_plano_concluido and has_conselho_concluido and has_fundo_cultura_concluido and has_orgao_gestor_concluido
        context['has_prazo_vencido'] = self.get_valida_prazo_vencido(
            sistema) and not (len(['componentes_restantes']) > 0)

        context['has_pendente_analise'] = (has_legislacao_arquivo and not has_legislacao_concluido) or (
            has_fundo_cultura_arquivo and not has_fundo_cultura_concluido) or (
            has_plano_arquivo and not has_plano_concluido) or (
            has_conselho_lei_arquivo and not has_conselho_lei_concluido)

        context[
            'has_componente_sistema'] = has_legislacao_concluido and has_plano_concluido and has_fundo_cultura_concluido and has_conselho_lei_concluido and has_orgao_gestor_concluido
        context['has_componente_sistema_conselho'] = has_conselho_concluido and has_comprovante_cnpj_concluido

        context['not_has_cadastrador'] = sistema.cadastrador is None
        context['not_has_dados_cadastrais'] = sistema.estado_processo == '0'
        context['not_has_documentacao'] = not (
            has_gestor_termo_posse and has_gestor_cpf_copia and has_gestor_rg_copia)
        context['has_formalizar_adesao'] = sistema.estado_processo == '3'
        context['has_fase_institucionalizar'] = has_legislacao_concluido and has_fundo_cultura_concluido

        return context

    def get_descricao_componente(self, id):
        return LISTA_TIPOS_COMPONENTES[id][1]

    def get_valida_arquivo(self, field):
        return bool(field) and bool(field.arquivo)

    def get_valida_documento_gestor(self, field):
        return bool(field) and bool(field.url)

    def get_valida_arquivo_concluido(self, field):
        return self.get_valida_arquivo(field) and field.situacao in (2, 3)

    def get_valida_prazo_vencido(self, sistema, ano=2):
        data_final_publicacao_acordo = None

        if not sistema.conferencia_nacional and sistema.data_publicacao_acordo is not None:
            try:
                data_final_publicacao_acordo = date(sistema.data_publicacao_acordo.year + ano,
                                                    sistema.data_publicacao_acordo.month,
                                                    sistema.data_publicacao_acordo.day)
            except ValueError:
                data_final_publicacao_acordo = date(sistema.data_publicacao_acordo.year + ano,
                                                    sistema.data_publicacao_acordo.month,
                                                    sistema.data_publicacao_acordo.day - 1)

        return not sistema.conferencia_nacional and data_final_publicacao_acordo is not None and data_final_publicacao_acordo < date.today()


class DetalharPlano(DetailView, LookUpAnotherFieldMixin):
    model = SistemaCultura
    context_object_name = "ente"
    template_name = "detalhe_plano.html"
    pk_url_kwarg = "cod_ibge"
    lookup_field = "ente_federado__cod_ibge"
    queryset = SistemaCultura.sistema.all()

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        sistema = context['object']
        context['historico'] = sistema.historico_cadastradores()[:10]
        context['historico_contatos'] = sistema.contatos.all()
        if sistema.sede:
            context['informacao_cnpj'] = Client().consulta_cnpj(sistema.sede.cnpj)

        sistema = self.get_queryset().get(id=self.object.id)

        context['componentes_restantes'] = []
        componentes = {
            0: "legislacao",
            1: "orgao_gestor",
            2: "fundo_cultura",
            3: "conselho",
            4: "plano",
        }

        for componente_id, componente_nome in componentes.items():
            componente_sistema = getattr(sistema, componente_nome, None)
            arquivo_componente = getattr(componente_sistema, 'arquivo', None)
            descricao = ''
            if not arquivo_componente:
                descricao = self.get_descricao_componente(componente_id)
                if componente_nome == 'fundo_cultura':
                    descricao += ' (Lei e Comprovante do CNPJ)'

                if componente_nome == 'conselho':
                    descricao += ' (Lei e Ata)'

                context['componentes_restantes'].append({
                    'nome': componente_nome,
                    'descricao': descricao
                })

        context['form'] = CadastradorEnte()

        # Validação dos documentos concluidos
        has_legislacao_concluido = self.get_valida_arquivo_concluido(sistema.legislacao)
        has_plano_concluido = self.get_valida_arquivo_concluido(sistema.plano)
        has_conselho_concluido = self.get_valida_arquivo_concluido(sistema.conselho)
        has_fundo_cultura_concluido = self.get_valida_arquivo_concluido(
            sistema.fundo_cultura)
        has_orgao_gestor_concluido = self.get_valida_arquivo_concluido(
            sistema.orgao_gestor)
        has_conselho_lei_concluido = bool(
            sistema.conselho) and self.get_valida_arquivo_concluido(sistema.conselho.lei)
        has_comprovante_cnpj_concluido = bool(sistema.fundo_cultura) and self.get_valida_arquivo_concluido(
            sistema.fundo_cultura.comprovante_cnpj)

        has_legislacao_arquivo = self.get_valida_arquivo(sistema.legislacao)
        has_plano_arquivo = self.get_valida_arquivo(sistema.plano)
        has_conselho_arquivo = self.get_valida_arquivo(sistema.conselho)
        has_fundo_cultura_arquivo = self.get_valida_arquivo(sistema.fundo_cultura)
        has_orgao_gestor_arquivo = self.get_valida_arquivo(sistema.orgao_gestor)
        has_conselho_lei_arquivo = bool(
            sistema.conselho) and self.get_valida_arquivo(sistema.conselho.lei)
        has_comprovante_cnpj_arquivo = bool(sistema.fundo_cultura) and self.get_valida_arquivo(
            sistema.fundo_cultura.comprovante_cnpj)

        has_gestor_termo_posse = bool(sistema.gestor) and self.get_valida_documento_gestor(
            sistema.gestor.termo_posse)
        has_gestor_cpf_copia = bool(sistema.gestor) and self.get_valida_documento_gestor(
            sistema.gestor.cpf_copia)
        has_gestor_rg_copia = bool(sistema.gestor) and self.get_valida_documento_gestor(
            sistema.gestor.rg_copia)

        # Situações do Ente Federado
        context['has_analise_nao_correcao'] = sistema.has_not_diligencias_enviadas_aprovadas() \
            and has_legislacao_concluido and has_plano_concluido \
            and has_conselho_concluido and has_fundo_cultura_concluido \
            and has_orgao_gestor_concluido

        context['has_prazo_vencido'] = self.get_valida_prazo_vencido(sistema)

        context['has_nenhum_componente_inserido'] = not (
            len(['componentes_restantes']) > 0)

        context['has_pendente_analise'] = (has_legislacao_arquivo and not has_legislacao_concluido) or (
            has_fundo_cultura_arquivo and not has_fundo_cultura_concluido) or (
            has_plano_arquivo and not has_plano_concluido) or (
            has_conselho_lei_arquivo and not has_conselho_lei_concluido)

        context[
            'has_componente_sistema'] = has_legislacao_concluido and has_plano_concluido and has_fundo_cultura_concluido and has_conselho_lei_concluido and has_orgao_gestor_concluido
        context['has_componente_sistema_conselho'] = has_conselho_concluido and has_comprovante_cnpj_concluido

        context['not_has_cadastrador'] = sistema.cadastrador is None
        context['not_has_dados_cadastrais'] = sistema.estado_processo == '0'
        context['not_has_documentacao'] = not (
            has_gestor_termo_posse and has_gestor_cpf_copia and has_gestor_rg_copia)
        context['has_formalizar_adesao'] = sistema.estado_processo == '3'
        context['has_fase_institucionalizar'] = has_legislacao_concluido and has_fundo_cultura_concluido

        return context

    def get_descricao_componente(self, id):
        return LISTA_TIPOS_COMPONENTES[id][1]

    def get_valida_arquivo(self, field):
        return bool(field) and bool(field.arquivo)

    def get_valida_documento_gestor(self, field):
        return bool(field) and bool(field.url)

    def get_valida_arquivo_concluido(self, field):
        return self.get_valida_arquivo(field) and field.situacao in (2, 3)

    def get_valida_prazo_vencido(self, sistema, ano=2):
        data_final_publicacao_acordo = None

        if not sistema.conferencia_nacional and sistema.data_publicacao_acordo is not None:
            try:
                data_final_publicacao_acordo = date(sistema.data_publicacao_acordo.year + ano,
                                                    sistema.data_publicacao_acordo.month,
                                                    sistema.data_publicacao_acordo.day)
            except ValueError:
                data_final_publicacao_acordo = date(sistema.data_publicacao_acordo.year + ano,
                                                    sistema.data_publicacao_acordo.month,
                                                    sistema.data_publicacao_acordo.day - 1)

        return not sistema.conferencia_nacional and data_final_publicacao_acordo is not None and data_final_publicacao_acordo < date.today()


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
        sistema = getattr(funcionario, 'sistema_cultura_gestor_cultura')
        return reverse_lazy('gestao:detalhar', kwargs={'cod_ibge': sistema.all()[0].ente_federado.cod_ibge})


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

    @method_decorator(user_passes_test(scdc_user_group_required))
    def dispatch(self, *args, **kwargs):
        return super(AlterarDadosEnte, self).dispatch(*args, **kwargs)


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




def alterar_usuario(request):
    field_name = request.POST.get('name', None)
    field_value = request.POST.get('value', None)
    id = request.POST.get('pk', None)

    try:
        kwargs = QueryDict(mutable=True)
        kwargs[field_name] = field_value
        user = User.objects.get(id=id)
        if field_name == 'is_staff' and int(field_value) == 1:
            group, created = Group.objects.get_or_create(name='usuario_scdc')
            group.user_set.add(user)
            field_value = True
        elif field_name == 'is_staff' and int(field_value) == 2:
            field_value = True
            user.groups.clear()
        elif field_name == 'is_staff' and int(field_value) == 0:
            field_value = False

        form = AlterarUsuarioForm(kwargs)
        if form.is_valid():
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


class CriarContato(CreateView):
    model = Contato
    form_class = CriarContatoForm
    template_name = "criar_contato.html"

    @method_decorator(user_passes_test(scdc_user_group_required))
    def dispatch(self, *args, **kwargs):
        return super(CriarContato, self).dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(CriarContato, self).get_form_kwargs()
        kwargs['sistema'] = SistemaCultura.objects.get(pk=self.kwargs['pk'])
        return kwargs

    def get_success_url(self):
        sistema = SistemaCultura.objects.get(pk=self.kwargs['pk'])
        return reverse_lazy('gestao:detalhar', kwargs={
            'cod_ibge': sistema.ente_federado.cod_ibge
        })


class InserirComponente(CreateView):
    @method_decorator(user_passes_test(scdc_user_group_required))
    def dispatch(self, *args, **kwargs):
        return super(InserirComponente, self).dispatch(*args, **kwargs)

    def get_template_names(self):
        componente = self.kwargs['componente']
        if componente == 'fundo_cultura' or componente == 'conselho' or componente == 'orgao_gestor' or componente == 'plano':
            return ['gestao/inserir_documentos/inserir_%s.html' % self.kwargs['componente']]
        return ['gestao/inserir_documentacao.html']

    def get_context_data(self, form=None, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.kwargs.get('pk')
        context['sistema'] = SistemaCultura.sistema.get(pk=pk)
        return context

    def get_form_kwargs(self):
        kwargs = super(InserirComponente, self).get_form_kwargs()
        pk = self.kwargs['pk']
        if self.kwargs['componente'] == 'orgao_gestor' or self.kwargs['componente'] == 'legislacao':
            kwargs['tipo'] = self.kwargs['componente']
        kwargs['sistema'] = SistemaCultura.sistema.get(pk=pk)
        kwargs['logged_user'] = self.request.user
        return kwargs

    def get_form_class(self):
        if self.kwargs['componente'] == 'fundo_cultura':
            form_class = CriarFundoForm
        elif self.kwargs['componente'] == 'orgao_gestor':
            form_class = CriarOrgaoGestorForm
        elif self.kwargs['componente'] == 'conselho':
            form_class = CriarConselhoForm
        elif self.kwargs['componente'] == 'plano':
            form_class = CriarPlanoForm
        else:
            form_class = CriarComponenteForm

        return form_class

    def get_success_url(self):
        pk = self.kwargs['pk']
        sistema = SistemaCultura.sistema.get(pk=pk)
        return reverse_lazy('gestao:detalhar', kwargs={
            'cod_ibge': sistema.ente_federado.cod_ibge
        })


class AlterarComponente(UpdateView):
    form_class = AlterarComponenteForm
    model = Componente

    @method_decorator(user_passes_test(scdc_user_group_required))
    def dispatch(self, *args, **kwargs):
        return super(AlterarComponente, self).dispatch(*args, **kwargs)

    def get_template_names(self):
        componente = self.kwargs['componente']
        if componente == 'fundo_cultura' or componente == 'conselho':
            return ['gestao/inserir_documentos/inserir_%s.html' % self.kwargs['componente']]
        return ['gestao/inserir_documentacao.html']

    def get_context_data(self, form=None, **kwargs):
        context = super().get_context_data(**kwargs)
        kwgs = {'{0}'.format(
            self.kwargs['componente']): self.kwargs.get('pk')}

        context['sistema'] = SistemaCultura.sistema.get(
            **kwgs)
        return context

    def get_success_url(self):
        kwgs = {'{0}'.format(
            self.kwargs['componente']): self.kwargs.get('pk')}
        ente_pk = SistemaCultura.sistema.get(
            **kwgs).ente_federado.cod_ibge
        return reverse_lazy(
            'gestao:detalhar',
            kwargs={'cod_ibge': ente_pk})


class AlterarConselhoCultura(AlterarConselhoCultura):
    form_class = CriarConselhoForm
    model = ConselhoDeCultura
    template_name = 'gestao/inserir_documentos/inserir_conselho.html'

    @method_decorator(user_passes_test(scdc_user_group_required))
    def dispatch(self, *args, **kwargs):
        return super(AlterarConselhoCultura, self).dispatch(*args, **kwargs)

    def get_context_data(self, form=None, **kwargs):
        context = super().get_context_data(**kwargs)
        kwgs = {'conselho': self.kwargs.get('pk')}

        context['sistema'] = SistemaCultura.sistema.get(
            **kwgs)
        return context

    def get_success_url(self):
        kwgs = {'conselho': self.kwargs.get('pk')}
        ente_pk = SistemaCultura.sistema.get(
            **kwgs).ente_federado.cod_ibge
        return reverse_lazy(
            'gestao:detalhar',
            kwargs={'cod_ibge': ente_pk})


class AlterarPlanoCultura(AlterarPlanoCultura):
    model = PlanoDeCultura
    form_class = CriarPlanoForm
    template_name = 'gestao/inserir_documentos/inserir_plano.html'

    @method_decorator(user_passes_test(scdc_user_group_required))
    def dispatch(self, *args, **kwargs):
        return super(AlterarPlanoCultura, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        kwgs = {'plano': self.kwargs.get('pk')}
        ente_pk = SistemaCultura.sistema.get(
            **kwgs).ente_federado.cod_ibge
        return reverse_lazy(
            'gestao:detalhar',
            kwargs={'cod_ibge': ente_pk})


class AlterarFundoCultura(AlterarFundoCultura):
    form_class = CriarFundoFormGestao
    model = FundoDeCultura
    template_name = 'gestao/inserir_documentos/inserir_fundo_cultura.html'

    @method_decorator(user_passes_test(scdc_user_group_required))
    def dispatch(self, *args, **kwargs):
        return super(AlterarFundoCultura, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        kwgs = {'fundo_cultura': self.kwargs.get('pk')}
        ente_pk = SistemaCultura.sistema.get(
            **kwgs).ente_federado.cod_ibge
        return reverse_lazy(
            'gestao:detalhar',
            kwargs={'cod_ibge': ente_pk})




class AlterarOrgaoGestor(AlterarOrgaoGestor):
    form_class = CriarOrgaoGestorFormGestao
    model = OrgaoGestor2
    template_name = 'gestao/inserir_documentos/inserir_orgao_gestor.html'

    @method_decorator(user_passes_test(scdc_user_group_required))
    def dispatch(self, *args, **kwargs):
        return super(AlterarOrgaoGestor, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        kwgs = {'orgao_gestor': self.kwargs.get('pk')}
        ente_pk = SistemaCultura.sistema.get(
            **kwgs).ente_federado.cod_ibge
        return reverse_lazy(
            'gestao:detalhar',
            kwargs={'cod_ibge': ente_pk})


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

    @method_decorator(user_passes_test(scdc_user_group_required))
    def dispatch(self, *args, **kwargs):
        return super(DiligenciaComponenteView, self).dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(DiligenciaComponenteView, self).get_form_kwargs()
        kwargs['arquivo'] = self.kwargs['arquivo']
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
        if self.kwargs['arquivo'] == 'arquivo':
            context['arquivo'] = componente.arquivo
        else:
            context['arquivo'] = getattr(componente, self.kwargs['arquivo']).arquivo
        context['ente_federado'] = ente_federado
        context['sistema_cultura'] = self.get_sistema_cultura()
        context['data_envio'] = self.get_componente().data_envio
        context['componente'] = componente
        context['historico_diligencias_componentes'] = self.get_sistema_cultura().get_componentes_diligencias(
            componente=self.kwargs['componente'],
            arquivo=self.kwargs['arquivo'])
        return context

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form), status=400)


class AlterarDiligenciaComponenteView(DiligenciaComponenteView, UpdateView):
    template_name = 'diligencia.html'
    model = DiligenciaSimples
    form_class = DiligenciaComponenteForm
    context_object_name = "diligencia"

    @method_decorator(user_passes_test(scdc_user_group_required))
    def dispatch(self, *args, **kwargs):
        return super(AlterarDiligenciaComponenteView, self).dispatch(*args, **kwargs)

    def get_sistema_cultura(self):
        return get_object_or_404(SistemaCultura, pk=int(self.kwargs['ente']))


class DiligenciaGeralCreateView(TemplatedEmailFormViewMixin, CreateView):
    template_name = 'diligencia.html'
    model = DiligenciaSimples
    form_class = DiligenciaGeralForm

    templated_email_template_name = "diligencia"
    templated_email_from_email = "naoresponda@turismo.gov.br"
    templated_email_bcc_email = "snc@turismo.gov.br"

    @method_decorator(user_passes_test(scdc_user_group_required))
    def dispatch(self, *args, **kwargs):
        return super(DiligenciaGeralCreateView, self).dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(DiligenciaGeralCreateView, self).get_form_kwargs()
        kwargs['sistema_cultura'] = self.get_sistema_cultura()
        kwargs['usuario'] = self.request.user.usuario

        return kwargs

    def get_context_data(self, form=None, **kwargs):
        sistema = self.get_sistema_cultura()

        context = super().get_context_data(**kwargs)
        context['sistema_cultura'] = sistema
        context['situacoes'] = sistema.get_situacao_componentes()
        context['historico_diligencias'] = self.get_historico_diligencias()
        context['historico_diligencias_componentes'] = sistema.get_componentes_diligencias()

        return context

    def get_historico_diligencias(self):
        historico_diligencias = DiligenciaSimples.objects.filter(
            sistema_cultura__ente_federado__cod_ibge=self.get_sistema_cultura()
            .ente_federado.cod_ibge)

        return historico_diligencias

    def get_sistema_cultura(self):
        return get_object_or_404(SistemaCultura, pk=int(self.kwargs['pk']))

    def templated_email_get_recipients(self, form):
        recipient_list = []

        if self.get_sistema_cultura().cadastrador:
            recipient_list = [self.get_sistema_cultura().cadastrador.user.email,
                              self.get_sistema_cultura().cadastrador.email_pessoal]

        if self.get_sistema_cultura().gestor:
            recipient_list.append(self.get_sistema_cultura().gestor.email_pessoal)
            recipient_list.append(self.get_sistema_cultura().gestor.email_institucional)

        recipient_list.append('snc@turismo.gov.br')
        return recipient_list

    def templated_email_get_send_email_kwargs(self, valid, form):
        if valid:
            context = self.templated_email_get_context_data(form_data=form.data)
        else:
            context = self.templated_email_get_context_data(form_errors=form.errors)
        try:
            from_email = self.templated_email_from_email()
        except TypeError:
            from_email = self.templated_email_from_email

        sistema = self.get_sistema_cultura()

        context['ente_federado'] = sistema.ente_federado
        context['situacoes'] = sistema.get_situacao_componentes()
        context['texto_diligencia'] = form.data['texto_diligencia']

        return {
            'template_name': self.templated_email_get_template_names(valid=valid),
            'from_email': from_email,
            'recipient_list': self.templated_email_get_recipients(form),
            'context': context,
            'bcc': [self.templated_email_bcc_email]
        }

    def get_success_url(self):
        return reverse_lazy("gestao:detalhar", kwargs={
            "cod_ibge": self.get_sistema_cultura().ente_federado.cod_ibge})


class DiligenciaGeralDetailView(DetailView):
    model = SistemaCultura
    fields = ['diligencia']
    template_name = 'diligencia.html'

    @method_decorator(user_passes_test(scdc_user_group_required))
    def dispatch(self, *args, **kwargs):
        return super(DiligenciaGeralDetailView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['sistema_cultura'] = self.object.id
        context['situacoes'] = self.object.get_situacao_componentes()
        return context


class SituacaoArquivoComponenteUpdateView(UpdateView):
    model = Componente
    fields = ['situacao']

    @method_decorator(user_passes_test(scdc_user_group_required))
    def dispatch(self, *args, **kwargs):
        return super(SituacaoArquivoComponenteUpdateView, self).dispatch(*args, **kwargs)


class DataTableEntes(BaseDatatableView):
    max_display_length = 150

    def ordering(self, qs):
        """ Get parameters from the request and prepare order by clause
        """
        # Number of columns that are used in sorting
        sorting_cols = 0
        if self.pre_camel_case_notation:
            try:
                sorting_cols = int(self._querydict.get('iSortingCols', 0))
            except ValueError:
                sorting_cols = 0
        else:
            sort_key = 'order[{0}][column]'.format(sorting_cols)
            while sort_key in self._querydict:
                sorting_cols += 1
                sort_key = 'order[{0}][column]'.format(sorting_cols)

        order = []
        order_columns = self.get_order_columns()

        for i in range(sorting_cols):
            # sorting column
            sort_dir = 'asc'
            try:
                if self.pre_camel_case_notation:
                    sort_col = int(self._querydict.get('iSortCol_{0}'.format(i)))
                    # sorting order
                    sort_dir = self._querydict.get('sSortDir_{0}'.format(i))
                else:
                    sort_col = int(self._querydict.get('order[{0}][column]'.format(i)))
                    # sorting order
                    sort_dir = self._querydict.get('order[{0}][dir]'.format(i))
            except ValueError:
                sort_col = 0

            sdir = '-' if sort_dir == 'desc' else ''
            sortcol = order_columns[sort_col]

            if isinstance(sortcol, list):
                for sc in sortcol:
                    order.append('{0}{1}'.format(sdir, sc.replace('.', '__')))
            else:
                order.append('{0}{1}'.format(sdir, sortcol.replace('.', '__')))

        if order:
            if "ente_federado" in order:
                return qs.order_by("ente_federado__nome")

            if "-ente_federado" in order:
                return qs.order_by("-ente_federado__nome")

            return qs.order_by(*order)

        return qs

    def get_initial_queryset(self):
        sistema = SistemaCultura.sistema.values_list('id', flat=True)

        return SistemaCultura.objects.filter(id__in=sistema).filter(
            ente_federado__isnull=False)

        return SistemaCultura.objects.filter(id__in=sistema)

    def filter_queryset(self, qs):
        search = self.request.POST.get('search[value]', None)
        custom_search = self.request.POST.get('columns[0][search][value]', None)
        componentes_search = self.request.POST.get('columns[1][search][value]', None)
        situacoes_search = self.request.POST.get('columns[2][search][value]', None)
        pendente_componentes_search = self.request.POST.get(
            'columns[3][search][value]', None)
        situacao_componentes_search = self.request.POST.get(
            'columns[4][search][value]', None)
        tipo_ente_search = self.request.POST.get('columns[5][search][value]', None)

        if search:
            query = Q()
            filtros_queryset = [
                Q(ente_federado__nome__unaccent__icontains=search),
                Q(gestor__nome__unaccent__icontains=search),
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

        if custom_search:
            qs = qs.filter(ente_federado__cod_ibge__startswith=custom_search)

        if componentes_search:
            componentes = {
                0: "legislacao",
                1: "orgao_gestor",
                2: "fundo_cultura",
                3: "conselho",
                4: "plano",
            }

            componentes_search = componentes_search.split(',')

            for id in componentes_search:
                nome_componente = componentes.get(int(id))
                kwargs = {'{0}__situacao__in'.format(nome_componente): [2, 3]}
                qs = qs.filter(**kwargs)

        if pendente_componentes_search:
            componentes = {
                0: "legislacao",
                1: "orgao_gestor",
                2: "fundo_cultura",
                3: "conselho",
                4: "plano",
            }

            pendente_componentes_search = pendente_componentes_search.split(',')

            for id in pendente_componentes_search:
                nome_componente = componentes.get(int(id))
                kwargs_dou = {'{0}__estado_processo__in': [6]}
                kwargs_pendentes = {'{0}__situacao__in'.format(nome_componente): [1]}
                kwargs_arquivos = {'{0}__arquivo'.format(nome_componente): ''}
                qs = qs.filter(**kwargs_pendentes,
                               estado_processo__in=['6']).exclude(**kwargs_arquivos)

        if situacao_componentes_search:
            componentes = {
                0: "legislacao",
                1: "orgao_gestor",
                2: "fundo_cultura",
                3: "conselho",
                4: "plano",
            }

            situacao_componentes_search = situacao_componentes_search.split(',')

            kwargs_legislacao = {'{0}__situacao__in'.format(
                componentes.get(0)): situacao_componentes_search}
            kwargs_orgao_gestor = {'{0}__situacao__in'.format(
                componentes.get(1)): situacao_componentes_search}
            kwargs_fundo_cultura = {'{0}__situacao__in'.format(
                componentes.get(2)): situacao_componentes_search}
            kwargs_conselho = {'{0}__situacao__in'.format(
                componentes.get(3)): situacao_componentes_search}
            kwargs_plano = {'{0}__situacao__in'.format(
                componentes.get(4)): situacao_componentes_search}

            qs = qs.filter(Q(**kwargs_legislacao) | Q(**kwargs_orgao_gestor) | Q(**kwargs_fundo_cultura) | Q(
                **kwargs_conselho) | Q(
                **kwargs_plano)).exclude()

        if situacoes_search:
            situacoes_search = situacoes_search.split(',')
            qs = qs.filter(estado_processo__in=situacoes_search)

        if tipo_ente_search:
            if tipo_ente_search == 'municipio':
                qs = qs.filter(ente_federado__cod_ibge__gte=99)
            elif tipo_ente_search == 'estado':
                qs = qs.filter(ente_federado__cod_ibge__lte=99)

        return qs

    def prepare_results(self, qs):
        json_data = []

        for item in qs:
            json_data.append([
                escape(item.id),
                escape(item.ente_federado),
                escape(item.gestor.nome) if item.gestor else '',
                escape(item.get_estado_processo_display()),
                escape(item.ente_federado.cod_ibge) if item.ente_federado else '',
                escape(
                    item.gestor.termo_posse.url if item.gestor and item.gestor.termo_posse else ''
                ),
                escape(item.data_publicacao_acordo.strftime("%d/%m/%Y")
                       ) if item.data_publicacao_acordo else '',
                escape(item.get_situacao_componentes())
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
                    "%d/%m/%Y") if item.data_publicacao_acordo else '',
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

            search_bool_field['is_staff'] = True if search_lower in 'administrador' \
                or search_lower in 'central de relacionamento' else False \
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

            if search_bool_field['is_staff'] \
                    and search_lower in 'central de relacionamento':
                ids = qs.values_list('id', flat=True)
                qs = Usuario.objects.filter(id__in=ids).exclude(
                    user__groups__name='usuario_scdc')

            if search_bool_field['is_staff'] and search_lower in 'administrador':
                ids = qs.values_list('id', flat=True)
                qs = Usuario.objects.filter(id__in=ids).filter(
                    user__groups__name='usuario_scdc')

        return qs

    def prepare_results(self, qs):
        json_data = []
        for item in qs:
            entes = []
            sistemas = SistemaCultura.sistema.filter(cadastrador=item.id)
            for sistema in sistemas:
                entes.append([
                    sistema.ente_federado.cod_ibge,
                    sistema.ente_federado.nome
                ])

            tipo_perfil = ''
            if not item.user.is_staff:
                tipo_perfil = 'Cadastrador'
            elif item.user.is_staff == True and not item.user.groups.filter(name='usuario_scdc').count() == 0:
                tipo_perfil = 'Administrador'
            elif item.user.is_staff == True and item.user.groups.filter(name='usuario_scdc').count() == 0:
                tipo_perfil = 'Central de Relacionamento'

            json_data.append([
                item.user.id,
                item.user.username,
                item.nome_usuario,
                item.user.email,
                item.user.last_login if item.user.last_login else '',
                'Ativo' if item.user.is_active else 'Inativo',
                tipo_perfil,
                entes,
                item.user.date_joined,

            ])
        return json_data


class DataTablePlanoTrabalho(BaseDatatableView):
    @method_decorator(user_passes_test(scdc_user_group_required))
    def dispatch(self, *args, **kwargs):
        return super(DataTablePlanoTrabalho, self).dispatch(*args, **kwargs)

    def get_initial_queryset(self):
        sistemas = SistemaCultura.sistema.values_list('id', flat=True)
        sistemas = SistemaCultura.objects.filter(id__in=sistemas, estado_processo='6')
        componente = self.request.POST.get('componente', None)

        if componente == 'conselho':
            sistemas = sistemas.filter((Q(conselho__lei__situacao=1)
                                        & ~Q(conselho__lei__arquivo='')) |
                                       (Q(conselho__situacao=1) & ~Q(conselho__arquivo='')))
        else:
            kwargs = {'{0}__situacao'.format(componente): 1}
            sistemas = sistemas.filter(**kwargs)
            kwargs = {'{0}__arquivo'.format(componente): ''}
            sistemas = sistemas.exclude(**kwargs)

        return sistemas

    def filter_queryset(self, qs):
        search = self.request.POST.get('search[value]', None)
        componente = self.request.POST.get('componente', None)

        where = Q(ente_federado__nome__unaccent__icontains=search)
        where |= Q(sede__cnpj__contains=search)

        if componente == 'fundo_cultura':
            where |= Q(fundo_cultura__cnpj__contains=search)

        if search:
            qs = qs.filter(where)

        return qs

    def prepare_results(self, qs):
        json_data = []
        componente = self.request.POST.get('componente', None)
        for item in qs:
            json_response = [
                item.id,
                item.ente_federado.__str__(),
                escape(item.sede.cnpj) if item.sede else '',
                getattr(item, componente).arquivo.url if getattr(
                    item, componente).arquivo else '',
                componente,
            ]
            if (componente == 'fundo_cultura'):
                json_response[2] = [
                    escape(item.sede.cnpj) if item.sede else '',
                    escape(item.fundo_cultura.cnpj) if item.fundo_cultura.cnpj else '',
                ]
                if getattr(item.fundo_cultura, 'comprovante_cnpj', None):
                    json_response.append(
                        item.fundo_cultura.comprovante_cnpj.arquivo.url
                    )

            if getattr(getattr(item, componente), 'lei', None):
                json_response.append(
                    getattr(item, componente).lei.arquivo.url
                )

            json_data.append(json_response)

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

class DetalharSolicitacaoCadastrador(DetailView):
    template_name = "detalhe_solicitacao_cadastrador.html"
    context_object_name = "solicitacao"
    queryset = TrocaCadastrador.objects.all()

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        sistema = context['object']
        sistema = self.get_queryset().get(id=self.object.id)
        return context


class AnalisarSolicitacaoCadastrador(AlterarSistemaCultura):
    template_name = "alterar_solicitacao_cadastrador.html"

    def get_success_url(self):
        sistema = TrocaCadastrador.objects.get(id=self.kwargs['pk'])
        return reverse_lazy(
            'gestao:solicitacao_cadastrador',
            kwargs={'pk': sistema.id})

class DataTableTrocaCadastrador(BaseDatatableView):
    def get_initial_queryset(self):
        '''
        sistema = SistemaCultura.sistema.values_list('id', flat=True)

        return SistemaCultura.objects.filter(id__in=sistema).filter(
            estado_processo='6',
            data_publicacao_acordo__isnull=False)
        '''
        return TrocaCadastrador.objects.all()

    def filter_queryset(self, qs):
        search = self.request.POST.get('search[value]', None)

        if search:
            return qs.filter(Q(ente_federado__nome__icontains=search))
        return qs

    def prepare_results(self, qs):
        json_data = []
        print(qs[1].get_status_display())
        for item in qs:
            json_data.append([
                item.id,
                escape(item.ente_federado),
                escape(item.alterado_por),
                item.alterado_em.strftime("%d/%m/%Y") if item.alterado_em else '',
                escape(item.get_status_display()),
            ])
        return json_data


    def get_success_url(self):
        sistema = SistemaCultura.objects.get(id=self.kwargs['pk'])
        return reverse_lazy(
            'gestao:detalhar',
            kwargs={'cod_ibge': sistema.ente_federado.cod_ibge})

class DataTableTrocaCadastrador(BaseDatatableView):
    def get_initial_queryset(self):
        '''
        sistema = SistemaCultura.sistema.values_list('id', flat=True)

        return SistemaCultura.objects.filter(id__in=sistema).filter(
            estado_processo='6',
            data_publicacao_acordo__isnull=False)
        '''
        return TrocaCadastrador.objects.all()

    def filter_queryset(self, qs):
        search = self.request.POST.get('search[value]', None)

        if search:
            where = \
                Q(ente_federado__nome__unaccent__icontains=search)
            if search.isdigit():
                where |= Q(prazo=search)
            return qs.filter(where)
        return qs

    def prepare_results(self, qs):
        json_data = []
        print(qs[1].get_status_display())
        for item in qs:
            json_data.append([
                item.id,
                escape(item.ente_federado),
                escape(item.alterado_por),
                item.alterado_em.strftime("%d/%m/%Y") if item.alterado_em else '',
                escape(item.get_status_display()),
            ])
        return json_data


def alterar_solicitacao_cadastrador(request):
    if request.method == "POST":
        id = request.POST.get('id', None)
        solicitacao = TrocaCadastrador.objects.get(id=id)

        solicitacao.laudo = request.POST.get('laudo', None)
        solicitacao.status = request.POST.get('status', None)
        solicitacao.save()

        print(solicitacao.status)
    return JsonResponse(data={}, status=200)

