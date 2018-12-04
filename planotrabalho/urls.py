from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from django.urls import path

from . import views

app_name = 'planotrabalho'

urlpatterns = [
    url(r'^(?P<pk>[0-9]+)/$',
        login_required(views.PlanoTrabalho.as_view()),
        name='planotrabalho'),

    path('componente/<str:tipo>',
        login_required(views.CadastrarComponente.as_view()),
        name='cadastrar_componente'),
    path('componente/fundo/<int:pk>',
        login_required(views.AlterarFundoCultura.as_view()),
        name='alterar_fundo'),
    path('componente/<str:tipo>/<int:pk>',
        login_required(views.AlterarComponente.as_view()),
        name='alterar_componente'),

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
    ]
