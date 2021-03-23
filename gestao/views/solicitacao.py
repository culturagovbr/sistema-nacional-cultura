from django_datatables_view.base_datatable_view import BaseDatatableView
from django.views.generic import DetailView, TemplateView
from django.utils.html import escape
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.db.models import Q
from templated_email import send_templated_mail

from django.http import HttpResponse, HttpResponseRedirect
from gestao.views.views import LookUpAnotherFieldMixin
from adesao.models import SolicitacaoDeTrocaDeCadastrador, SistemaCultura, Usuario

class BaseDataTableSolicitacao(BaseDatatableView):
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

        return SolicitacaoDeTrocaDeCadastrador.objects.all()

    def filter_queryset(self, qs):
        search = self.request.POST.get('search[value]', None)
        situacoes_search = self.request.POST.get('columns[4][search][value]', None)

        if search:
            query = Q()
            filtros_queryset = [
                Q(ente_federado__nome__unaccent__icontains=search),
                Q(alterado_por__nome_usuario__unaccent__icontains=search),
            ]

            for filtro in filtros_queryset:
                query |= filtro

            qs = qs.filter(query)
        
        if situacoes_search:
            situacoes_search = situacoes_search.split(',')
            qs = qs.filter(status__in=situacoes_search)

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
