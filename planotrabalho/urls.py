from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from django.urls import path
from django.conf import settings
from django.views.static import serve
from django.conf.urls.static import static

from . import views

app_name = 'planotrabalho'

urlpatterns = [
    url(r'^(?P<pk>[0-9]+)/$',
        login_required(views.PlanoTrabalho.as_view()),
        name='planotrabalho'),

    path('<int:pk>',login_required(views.PlanoTrabalho.as_view()),
        name='plano_trabalho'),
    path('componente/plano',
        login_required(views.CadastrarPlanoDeCultura.as_view()),
        name='cadastrar_plano'),
    path('componente/fundo_cultura',
        login_required(views.CadastrarFundoDeCultura.as_view()),
        name='cadastrar_fundo_cultura'),
    path('componente/orgao_gestor',
        login_required(views.CadastrarOrgaoGestor.as_view()),
        name='cadastrar_orgao'),
    path('componente/conselho',
        login_required(views.CadastrarConselhoDeCultura.as_view()),
        name='cadastrar_conselho'),
     path('componente/legislacao',
        login_required(views.CadastrarLegislacao.as_view()),
        name='cadastrar_legislacao'),
    path('componente/fundo/alterar/<int:pk>',
        login_required(views.AlterarFundoCultura.as_view()),
        name='alterar_fundo_cultura'),
    path('componente/orgao/alterar/<int:pk>',
        login_required(views.AlterarOrgaoGestor.as_view()),
        name='alterar_orgao'),
    path('componente/conselho/alterar/<int:pk>',
        login_required(views.AlterarConselhoCultura.as_view()),
        name='alterar_conselho'),
    path('componente/plano/alterar/<int:pk>',
        login_required(views.AlterarPlanoCultura.as_view()),
        name='alterar_plano'),
    path('componente/legislacao/alterar/<int:pk>',
        login_required(views.AlterarLegislacao.as_view()),
        name='alterar_legislacao'),

    url(r'^conselheiros/$',
        login_required(views.get_conselheiros),
        name='get_conselheiros'),
    path('<int:conselho>/conselheiro/criar',
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

if settings.DEBUG:
	urlpatterns += [
        url(r'^media/(?P<path>.*)$',
        serve, { 'document_root':
        settings.MEDIA_ROOT,}), ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
