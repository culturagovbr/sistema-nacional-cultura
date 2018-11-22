from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from django.urls import path

from django.contrib.auth.views import LoginView
from django.contrib.auth.views import LogoutView

from . import views


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

    # Cadastro e alteração de prefeitura
    url(r'^municipio/selecionar$', views.selecionar_tipo_ente,
        name='selecionar_tipo_ente'),
    url(r'^municipio/$', login_required(views.CadastrarMunicipio.as_view()),
        name='municipio'),
    url(r'^sucesso-cadastro-prefeitura/$',
        views.sucesso_municipio,
        name='sucesso_municipio'),
    url(r'^municipio/cadastrar/(?P<tipo_ente>\d+)/$',
        login_required(views.CadastrarMunicipio.as_view()),
        name='cadastrar_municipio'),
    url(r'^municipio/(?P<pk>[0-9]+)/$',
        login_required(views.AlterarMunicipio.as_view()),
        name='alterar_municipio'),

    # Cadastro e alteração de responsável
    path('sucesso-cadastro-funcionario/',
        views.sucesso_funcionario,
        name='sucesso_funcionario'),
    path('funcionario/<str:tipo>/<int:pk>',
        login_required(views.AlterarFuncionario.as_view()),
        name='alterar_funcionario'),
    url(r'^responsavel/(?P<pk>[0-9]+)/$',
        login_required(views.AlterarResponsavel.as_view()),
        name='alterar_responsavel'),
    url(r'^importar/secretario/$',
        views.importar_secretario,
        name='importar_secretario'),

    path('funcionario/<int:sistema>/<str:tipo>',
            login_required(views.CadastrarFuncionario.as_view()),
            name='cadastrar_funcionario'),
    path('sistema/cadastrar/',
            login_required(views.CadastrarSistemaCultura.as_view()),
            name='cadastrar_sistema'),
    path('sistema/alterar/<int:pk>',
            login_required(views.AlterarSistemaCultura.as_view()),
            name='alterar_sistema'),

    # Cadastro e alteração de secretário
   
    url(r'^sucesso-cadastro-secretario/$',
        views.sucesso_secretario,
        name='sucesso_secretario'),
    url(r'^secretario/(?P<pk>[0-9]+)/$',
        login_required(views.AlterarSecretario.as_view()),
        name='alterar_secretario'),

    # Cadastro e alteração de cadastrador
    url(r'^alterar/cadastrador/$',
        login_required(views.OficioAlteracao.as_view()),
        name='alterar_cadastrador'),

    # Minuta de acordo e termo de solicitação
    url(r'^termo/minuta/$',
        login_required(views.MinutaAcordo.as_view()),
        name='minuta'),
    url(r'^termo/solicitacao/$',
        login_required(views.TermoSolicitacao.as_view()),
        name='solicitacao'),
    url(r'^oficio/alteracao/$',
        login_required(views.OficioAlteracao.as_view()),
        name='alteracao'),

    # Consulta
    path('consultar/<str:tipo>', views.ConsultarEnte.as_view(), name='consultar'),
    url(r'^detalhar/(?P<pk>[0-9]+)$', views.Detalhar.as_view(), name='detalhar'),
    ]
