from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from django.urls import path

from . import views

app_name = 'planotrabalho'

urlpatterns = [
    url(r'^(?P<pk>[0-9]+)/$',
        login_required(views.PlanoTrabalho.as_view()),
        name='planotrabalho'),

    # Primeira etapa - Criação do Sistema de Cultura
    url(r'^sistema/$',
        login_required(views.CadastrarSistema.as_view()),
        name='sistema'),
    path('componente/<str:tipo>',
        login_required(views.CadastrarComponente.as_view()),
        name='cadastrar_componente'),
    url(r'^sistema/(?P<pk>[0-9]+)/$',
        login_required(views.AlterarSistema.as_view()),
        name='alterar_sistema'),

    # Segunda etapa - Estruturação do Orgão Gestor
    url(r'^gestor/$',
        login_required(views.CadastrarOrgaoGestor.as_view()),
        name='gestor'),
    url(r'^gestor/(?P<pk>[0-9]+)/$',
        login_required(views.AlterarOrgaoGestor.as_view()),
        name='alterar_gestor'),

    # Terceira etapa - Criação do Conselho de Política Cultural
    url(r'^conselho/$',
        login_required(views.CadastrarConselho.as_view()),
        name='conselho'),
    url(r'^conselho/(?P<pk>[0-9]+)/$',
        login_required(views.AlterarConselho.as_view()),
        name='alterar_conselho'),
    url(r'^conselheiros/$',
        login_required(views.get_conselheiros),
        name='get_conselheiros'),
    url(r'^conselheiro/criar/$',
        login_required(views.CriarConselheiro.as_view()),
        name="criar_conselheiro"),
    url(r'^conselheiro/listar/$',
        login_required(views.ListarConselheiros.as_view()),
        name="listar_conselheiros"),
    url(r'^conselheiro/editar/(?P<pk>[0-9]+)/$',
        login_required(views.AlterarConselheiro.as_view()),
        name="alterar_conselheiro"),
    url(r'^conselheiro/remover/(?P<pk>[0-9]+)/$',
        login_required(views.DesabilitarConselheiro.as_view()),
        name="remover_conselheiro"),



    # Quarta etapa - Criação do Fundo de Cultura
    url(r'^fundo/$',
        login_required(views.CadastrarFundo.as_view()),
        name='fundo'),
    url(r'^fundo/(?P<pk>[0-9]+)/$',
        login_required(views.AlterarFundo.as_view()),
        name='alterar_fundo'),

    # Quinta etapa - Elaboração do Plano de Cultura
    url(r'^plano/$',
        login_required(views.CadastrarPlano.as_view()),
        name='plano'),
    url(r'^plano/(?P<pk>[0-9]+)/$',
        login_required(views.AlterarPlano.as_view()),
        name='alterar_plano'),
    ]
