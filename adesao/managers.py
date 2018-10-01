from django.db import models


class BaseQuerySet(models.QuerySet):
    """ Faz com que as consultas sempre utilizem select_related() """

    def get_queryset(self):
        return self.select_related()
    

class SistemaManager(models.Manager):
    """ Manager utilizado para interações com os Sistemas de Cultura """

    def get_queryset(self):
        return BaseQuerySet.order_by('-data').distinct('ente_federado__cod_ibge')


class SistemaCulturaManager(models.Manager):
    def ativo(self, uf, cidade=None):
        """ Retorna último SistemaCultura ativo relativo a um ente federado """
        return self.filter(uf=uf, cidade=cidade).latest('data_criacao')

    def ativo_ou_cria(self, uf, cidade=None):
        """ Retorna último SistemaCultura ativo relativo a um ente federado
        caso ele não exista cria um novo SistemaCultura """
        try:
            sistema = self.ativo(uf=uf, cidade=cidade)
        except SistemaCultura.DoesNotExist:
            sistema = SistemaCultura.objects.create(uf=uf, cidade=cidade)
        return sistema

    def por_municipio(self, uf, cidade=None):
        """ Retorna todos os SistemaCultura de uma cidade ou estado """
        sistemas = self.filter(uf=uf, cidade=cidade).select_related('cadastrador', 'cidade', 'uf')

        return sistemas
