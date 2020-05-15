from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from django.urls import path

from django.contrib.auth.views import LoginView
from django.contrib.auth.views import LogoutView

from . import views

# verificacao de dados cadastrados
from django.contrib.auth.models import User
# Verificacao Json
from django.http import JsonResponse

app_name = "adesao"

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^sucesso-cadastro-usuario/$',
        views.sucesso_usuario,
        name='sucesso_usuario'),
    url(r'^login/$', LoginView.as_view(template_name='index.html'),
        name='login'),
    url(r'^sair/$', LogoutView.as_view(template_name='index.html'),
        name='logout'),
    url(r'^ativar/usuario/(?P<codigo>[\w]+)/$',
        views.ativar_usuario, name='ativar_usuario'),

    url(r'^home/', views.home, name='home'),
    url(r'^usuario/$', views.CadastrarUsuario.as_view(), name='usuario'),
    url(r'^faleconosco/$', views.fale_conosco, name='faleconosco'),
    url(r'^erro-impressao/$', views.erro_impressao, name='erro_impressao'),

    # Cadastro e alteração de prefeitura
    url(r'^municipio/selecionar$', views.selecionar_tipo_ente,
        name='selecionar_tipo_ente'),
    url(r'^sucesso-cadastro-prefeitura/$',
        views.sucesso_municipio,
        name='sucesso_municipio'),

    # Cadastro e alteração de responsável
    path('sucesso-cadastro-funcionario/', views.sucesso_funcionario, name='sucesso_funcionario'),
    path('funcionario/alterar/<int:pk>', login_required(views.AlterarFuncionario.as_view()), name='alterar_funcionario'),
    path('funcionario/<int:sistema>', login_required(views.CadastrarFuncionario.as_view()), name='cadastrar_funcionario'),
    path('sistema/cadastrar/', login_required(views.CadastrarSistemaCultura.as_view()), name='cadastrar_sistema'),
    path('sistema/alterar/<int:pk>', login_required(views.AlterarSistemaCultura.as_view()), name='alterar_sistema'),

    path('sistema', login_required(views.define_sistema_sessao), name='define_sistema_sessao'),

    # Minuta de acordo e termo de solicitação
    path('termo/<str:template>/<str:nome_arquivo>', login_required(views.GeraPDF.as_view()), name='gera_pdf'),

    # Consulta
    path('consultar/<str:tipo>', views.ConsultarEnte.as_view(), name='consultar'),
    path('detalhar/<int:cod_ibge>', views.Detalhar.as_view(), name='detalhar'),

    # Ajax/consultar Entederado
    # url(r'^ajax/validate_username/$', views.validate_username, name='validate_username'),
    path(r'^ajax/validate_username/$', views.validate_username, name='validate_username'),

    # consulta cnpj
    url(r'^ajax/validate_cnpj/$', views.validate_cnpj, name='validate_cnpj'),

]
