from rest_framework.pagination import LimitOffsetPagination
from rest_framework.utils.urls import replace_query_param
from rest_framework.response import Response
import sys


class HalLimitOffsetPagination(LimitOffsetPagination):

    # Limite máximo de objetos retornados por requisição
    max_limit = 100

    def get_paginated_response(self, data):
        if self.get_next_link():
            data['_links']['next'] = {'href': self.get_next_link()}
        if self.get_previous_link():
            data['_links']['previous'] = {'href': self.get_previous_link()}
        template_url = replace_query_param(
            self.request.build_absolute_uri(), self.limit_query_param, '_PAGE_')
        data['_links']['page'] = {
            # need this trick because of URL encoding
            'href': template_url.replace('_PAGE_', '{?page}'),
            'templated': True}
        data['count'] = self.count
        data['page_size'] = self.count \
            if self.request.query_params[self.limit_query_param] == '-1' else \
            self.get_limit(self.request)
        return Response(data)

    def get_limit(self, request):
        if request.query_params[self.limit_query_param] == '-1':
            return sys.maxsize
        return super().get_limit(request)
