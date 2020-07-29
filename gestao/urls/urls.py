from django.conf.urls import url
from django.urls import path, re_path, include
from django.contrib.admin.views.decorators import staff_member_required

from gestao.views import views, solicitacao_de_adesao, solicitacao_de_troca_de_cadastrador

app_name = 'gestao'

urlpatterns = [
    url(r'^solicitacao-de-adesao/', include('gestao.urls.solicitacao_de_adesao', namespace="solicitacao_de_adesao")),
    url(r'^solicitacao-de-troca-de-cadastrador/', include('gestao.urls.solicitacao_de_troca_de_cadastrador', namespace="solicitacao_de_troca_de_cadastrador")),
    
    # Acompanhar andamento dos processos de adesão
    path('', staff_member_required(
        views.dashboard,
        login_url='adesao:login'), name='dashboard'),
    path('entes', staff_member_required(
        views.AcompanharSistemaCultura.as_view(),
        login_url='adesao:login'), name='acompanhar_adesao'),
    path('ente/<int:cod_ibge>/dados-adesao',
         staff_member_required(views.AlterarDadosEnte.as_view()),
         name='alterar_dados_adesao'),
    path('alterar/<int:pk>',
         staff_member_required(views.AlterarDadosSistemaCultura.as_view()),
         name='alterar_sistema'),

    path('alterar/funcionario/<int:pk>',
         staff_member_required(views.AlterarFuncionario.as_view()),
         name='alterar_funcionario'),
    path('funcionario/<int:sistema>',
         staff_member_required(views.CadastrarFuncionario.as_view()),
         name='cadastrar_funcionario'),

    # Acompanhar e aditivar prazos dos municípios
    url(r'^acompanhar/prazo/',
        staff_member_required(views.AcompanharPrazo.as_view()), name='acompanhar_prazo'),
    url(r'^aditivar-prazo/',
        staff_member_required(views.aditivar_prazo, login_url='adesao:login'), name='aditivar_prazo'),

    # Acompanhar componentes
    path('plano-trabalho/',
         staff_member_required(views.plano_trabalho),
         name='plano_trabalho'),
    path('docs-componentes/',
         staff_member_required(views.listar_componentes),
         name='listar_componentes'),
    path('acompanhar/<str:componente>',
         staff_member_required(views.AcompanharComponente.as_view()),
         name='acompanhar_componente'),

    # Detalhar usuário
    path('ente/<int:cod_ibge>',
         staff_member_required(views.DetalharEnte.as_view()),
         name='detalhar'),

    path('plano/<int:cod_ibge>',
         staff_member_required(views.DetalharPlano.as_view()),
         name='detalhar'),
    # re_path(r'^detalhar/municipio/(?P<pk>[0-9]+)$',
    #     staff_member_required(views.DetalharEnte.as_view()),
    #     name='detalhar'),
    url(r'^usuarios/',
        staff_member_required(
            views.ListarUsuarios.as_view(),
            login_url='adesao:login'), name='usuarios'),
    url(r'^alterar/usuario/',
        staff_member_required(
            views.alterar_usuario,
            login_url='adesao:login'), name='alterar_usuario'),

    # UF e Município aninhados
    path("chain/ente",
         views.EnteChain.as_view(),
         name='ente_chain'),

    # Inserir de documentos de entes federados
    url(r'^inserir-documentos/ente-federado$',
        staff_member_required(views.ListarDocumentosEnteFederado.as_view()), name='inserir_entefederado'),
    path("inserir-documentos/ente-federado/alterar/<int:pk>",
         staff_member_required(views.AlterarDocumentosEnteFederado.as_view()), name='alterar_entefederado'),

    path("inserir-documentos/<str:componente>/<int:pk>", staff_member_required(
        views.InserirComponente.as_view(),
        login_url='adesao:login'), name='inserir_componente'),

    # Tela de alteração de upload do plano de trabalho
    path("inserir-documentos/plano/alterar/<int:pk>", staff_member_required(
        views.AlterarPlanoCultura.as_view(),
        login_url='adesao:login'), name='alterar_plano'),
    path("inserir-documentos/fundo_cultura/alterar/<int:pk>", staff_member_required(
        views.AlterarFundoCultura.as_view(),
        login_url='adesao:login'), name='alterar_fundo'),
    path("inserir-documentos/conselho/alterar/<int:pk>", staff_member_required(
        views.AlterarConselhoCultura.as_view(),
        login_url='adesao:login'), name='alterar_conselho'),
    path("inserir-documentos/orgao/alterar/<int:pk>", staff_member_required(
        views.AlterarOrgaoGestor.as_view(),
        login_url='adesao:login'), name='alterar_orgao'),
    path("inserir-documentos/<str:componente>/alterar/<int:pk>", staff_member_required(
        views.AlterarComponente.as_view(),
        login_url='adesao:login'), name='alterar_componente'),

    # Diligência de Componente

    # url(r'^(?P<pk>[0-9]+)/diligencia/(?P<componente>[A-z]+)/(?P<resultado>[0-1])',
    #     staff_member_required(views.DiligenciaComponenteView.as_view()), name="diligencia_componente"),

        
    # Rota para AlterarCadastrador
    path('ente/<int:cod_ibge>/alterarcadastrador',
         staff_member_required(views.AlterarCadastradorEnte.as_view()),
         name='alterar_cadastrador'),

    path("<int:pk>/diligencia/add",
         staff_member_required(views.DiligenciaGeralCreateView.as_view()),
         name="diligencia_geral_adicionar"),

    path("<int:pk>/diligencia/<str:componente>/<str:arquivo>",
         staff_member_required(views.DiligenciaComponenteView.as_view()),
         name="diligencia_componente"),

    path("<int:ente>/diligencia/<str:componente>/<str:arquivo>/<int:pk>",
         staff_member_required(
             views.AlterarDiligenciaComponenteView.as_view()),
         name="alterar_diligencia_componente"),

    path("<int:pk>/diligencia/<str:componente>/<int:pk_componente>/situacao",
         staff_member_required(views.SituacaoArquivoComponenteUpdateView.as_view()),
         name="componente_situacao_atualiza"),

    path("<int:pk>/diligencia",
         staff_member_required(views.DiligenciaGeralDetailView.as_view()),
         name="diligencia_geral"),

    path("<int:pk>/contato",
         staff_member_required(views.CriarContato.as_view()),
         name="criar_contato"),

    path("ajax/consultar_cpf",
         staff_member_required(views.ajax_consulta_cpf),
         name="ajax-consulta-cpf"),

    # ajax leaflet
    url(r'^ajax-consulta-entes$', staff_member_required(views.ajax_consulta_entes),
        name='ajax_consulta_entes'),

    # ajax datatable
    url(r'^datatable-entes$', staff_member_required(views.DataTableEntes.as_view()),
        name='ajax_entes'),
    url(r'^datatable-prazo$', staff_member_required(views.DataTablePrazo.as_view()),
        name='ajax_prazo'),
    url(r'^datatable-usuarios$', staff_member_required(views.DataTableUsuarios.as_view()),
        name='ajax_usuarios'),
    url(r'^datatable-plano-trabalho$', staff_member_required(views.DataTablePlanoTrabalho.as_view()),
        name='ajax_plano_trabalho'),
    url(r'^datatable-docs-componentes$', staff_member_required(views.DataTableListarDocumentos.as_view()),
        name='ajax_docs_componentes'),

]

