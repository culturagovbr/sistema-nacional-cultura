from django.db import models
from django.core.exceptions import EmptyResultSet


class SistemaManager(models.Manager):
    """ Manager utilizado para interações com os Sistemas de Cultura """

    def get_queryset(self):
        return super().get_queryset().distinct('ente_federado').select_related()


class HistoricoManager(models.Manager):
    """
    Manager responsavel pelo gerenciamento de histórico de um determinado ente federado.
    """

    def ente(self, cod_ibge=None):
        """ Retorna o histórico de um ente federado """
        if not cod_ibge:
            raise EmptyResultSet

        return self.filter(ente_federado__cod_ibge=cod_ibge)
