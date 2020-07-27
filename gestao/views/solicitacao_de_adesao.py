from django_datatables_view.base_datatable_view import BaseDatatableView
from django.views.generic import DetailView, TemplateView
from django.utils.html import escape
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone

from templated_email import send_templated_mail

from django.http import HttpResponse, HttpResponseRedirect
from gestao.views.views import LookUpAnotherFieldMixin
from adesao.models import SolicitacaoDeAdesao, SistemaCultura, Usuario

class DataTableSolicitacaoDeAdesao(BaseDatatableView):
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
        #sistema = SistemaCultura.sistema.values_list('id', flat=True)

        return SolicitacaoDeAdesao.objects.all()

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
                #Q(gestor__nome__unaccent__icontains=search),
            ]

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
                escape(item.alterado_por.nome_usuario) if item.alterado_por else '',
                escape(item.alterado_em.strftime("%d/%m/%Y")) if item.alterado_em else '',
                escape(item.status),
            ])
        return json_data


class DetalharSolicitacao(DetailView, LookUpAnotherFieldMixin):
    model = SolicitacaoDeAdesao
    template_name = "solicitacaodeadesao_detail.html"

def processar_solicitacao(request, pk, status_solicitacao, status_sistema, email_template):
    solicitacao = SolicitacaoDeAdesao.objects.get(pk=pk)
    solicitacao.avaliador = Usuario.objects.get(user__pk=request.user.id) 
    solicitacao.data_analise = timezone.now()
    solicitacao.status = status_solicitacao
    solicitacao.save()
    '''
    sc = SistemaCultura.sistema.get(ente_federado__cod_ibge=solicitacao.ente_federado.cod_ibge)
    sc.estado_processo = status_sistema
    sc.save()
    '''
    send_templated_mail(
        template_name=email_template,
        from_email='naoresponda@turismo.gov.br',
        recipient_list=[solicitacao.alterado_por.user.email],
        context={
            'cadastrador':solicitacao.alterado_por.nome_usuario,
            'ente_federado':solicitacao.ente_federado.nome,
            'motivo':request.POST.get('justificativa'),
        },)

    return solicitacao

def aprovar_solicitacao(request, pk):
    processar_solicitacao(request, pk, '1', '6', 'adesao_aprovada')
    
    return HttpResponseRedirect(reverse('gestao:solicitacao_de_adesao:list'))


def rejeitar_solicitacao(request, pk):
    solicitacao = processar_solicitacao(request, pk, '2', '1', 'adesao_reprovada')
    solicitacao.laudo = request.POST['justificativa']
    solicitacao.save()
    
    return HttpResponseRedirect(reverse('gestao:solicitacao_de_adesao:list'))

class SolicitacaoDeAdesaoList(TemplateView):
    template_name = 'solicitacaodeadesao_list.html'

