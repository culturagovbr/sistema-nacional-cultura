from django.contrib import admin

# Importando os models
from .models import Municipio, Responsavel, Secretario, Usuario, EnteFederado, Funcionario, SolicitacaoDeAdesao


# Mostrando no datagrid Municipio
class MunicipioAdmin(admin.ModelAdmin):
    # nome coluna
    list_display = ('nome_prefeito', 'cnpj_prefeitura', 'cidade', 'estado')
    # links
    list_display_links = ('nome_prefeito', 'cidade')
    # filtros
    # list_filter = ('nome_prefeito', 'cidade')
    # paginas
    list_per_page = 25
    # pesquisa
    # search_fields = ['nome_prefeito', 'cidade']


# Mostrando no datagrid Responsavel
class ResponsavelAdmin(admin.ModelAdmin):
    list_display = ('nome_responsavel', 'cargo_responsavel', 'instituicao_responsavel')


# Mostrando no datagrid Ente Federado
class EnteFederadoAdmin(admin.ModelAdmin):
    list_display = ('cod_ibge', 'nome')


# Mostrando no datagrid Ente Federado
class FuncionarioAdmin(admin.ModelAdmin):
    list_display = ('cpf', 'nome', 'cargo')


# Registrando no Admin o model e mostrando os campos
admin.site.register(Municipio, MunicipioAdmin)
admin.site.register(Responsavel, ResponsavelAdmin)
admin.site.register(Secretario)
admin.site.register(Usuario)
admin.site.register(EnteFederado, EnteFederadoAdmin)
admin.site.register(Funcionario, FuncionarioAdmin)
admin.site.register(SolicitacaoDeAdesao)