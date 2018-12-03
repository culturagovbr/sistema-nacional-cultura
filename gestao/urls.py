from django.conf.urls import url
from django.urls import path, re_path
from django.contrib.admin.views.decorators import staff_member_required

from . import views

app_name = 'gestao'

urlpatterns = [
    # Acompanhar andamento dos processos de adesão
    path('', staff_member_required(
        views.AcompanharSistemaCultura.as_view(),
        login_url='adesao:login'), name='acompanhar_adesao'),
    path('ente/<int:cod_ibge>/dados-adesao',
        staff_member_required(views.AlterarDadosEnte.as_view()),
        name='alterar_dados_adesao'),
    
    # Rota para AlterarCadastrador
    path('ente/<int:cod_ibge>/alterarcadastrador',
        staff_member_required(views.AlterarCadastradorEnte.as_view()),
        name='alterar_cadastrador'),

    # Acompanhar e aditivar prazos dos municípios
    url(r'^acompanhar/prazo/',
        staff_member_required(views.AcompanharPrazo.as_view()), name='acompanhar_prazo'),
     url(r'^aditivar/prazo/(?P<id>[\w]+)/(?P<page>[\w]+)$',
        staff_member_required(views.aditivar_prazo, login_url='adesao:login'), name='aditivar_prazo'),
    
    # Acompanhar componentes
    path('acompanhar/<str:componente>',
            staff_member_required(views.AcompanharComponente.as_view()),
            name='acompanhar_componente'),

    # Diligência no anexo
    url(r'^diligencia/(?P<etapa>[\w]+)/(?P<st>[\w]+)/(?P<id>[\w]+)$',
        staff_member_required(
            views.diligencia_documental,
            login_url='adesao:login'), name='diligencia_documental'),
    # Conclusão da etapa
    url(r'^concluir/(?P<etapa>[\w]+)/(?P<st>[\w]+)/(?P<id>[\w]+)$',
        staff_member_required(
            views.concluir_etapa,
            login_url='adesao:login'), name='concluir_etapa'),
    # Situação da Avaliação = '3'
    url(r'^reprovar/(?P<etapa>[\w]+)/(?P<st>[\w]+)/(?P<id>[\w]+)$',
        staff_member_required(
            views.situacao_3,
            login_url='adesao:login'), name='situacao_3'),
    # Situação da Avaliação = '4'
    url(r'^reprovar4/(?P<etapa>[\w]+)/(?P<st>[\w]+)/(?P<id>[\w]+)$',
        staff_member_required(
            views.situacao_4,
            login_url='adesao:login'), name='situacao_4'),
    # Situação da Avaliação = '5'
    url(r'^reprovar5/(?P<etapa>[\w]+)/(?P<st>[\w]+)/(?P<id>[\w]+)$',
        staff_member_required(
            views.situacao_5,
            login_url='adesao:login'), name='situacao_5'),
    # Situação da Avaliação = '6'
    url(r'^reprovar6/(?P<etapa>[\w]+)/(?P<st>[\w]+)/(?P<id>[\w]+)$',
        staff_member_required(
            views.situacao_6,
            login_url='adesao:login'), name='situacao_6'),

    # Detalhar usuário
    path('ente/<int:cod_ibge>',
            staff_member_required(views.DetalharEnte.as_view()),
            name='detalhar'),
    # re_path(r'^detalhar/municipio/(?P<pk>[0-9]+)$',
    #     staff_member_required(views.DetalharEnte.as_view()),
    #     name='detalhar'),
    url(r'^usuarios/',
        staff_member_required(
            views.ListarUsuarios.as_view(),
            login_url='adesao:login'), name='usuarios'),
    url(r'^alterar/usuario/(?P<pk>[\d]+)$',
        staff_member_required(
            views.AlterarUsuario.as_view(),
            login_url='adesao:login'), name='alterar_usuario'),

    # UF e Município aninhados
    path("chain/ente",
        views.EnteChain.as_view(),
        name='ente_chain'),

    url(r'^chain/cidade$',
        views.CidadeChain.as_view(),
        name='cidade_chain'),

    url(r'^chain/uf$',
        views.UfChain.as_view(),
        name='uf_chain'),

    # Inserir de documentos de entes federados
    url(r'^inserir-documentos/ente-federado$',
        staff_member_required(views.ListarDocumentosEnteFederado.as_view()), name='inserir_entefederado'),
    url(r'^inserir-documentos/ente-federado/alterar/(?P<pk>[0-9]+)$',
        staff_member_required(views.AlterarDocumentosEnteFederado.as_view()), name='alterar_entefederado'),

    path("inserir-documentos/<str:componente>/<int:pk>", staff_member_required(
        views.InserirComponente.as_view(),
        login_url='adesao:login'), name='inserir_componente'), 
    # Inserção de documentos da criação do sistema de cultura
    url(r'^listar-documentos/(?P<template>\w+)$', staff_member_required(
        views.ListarDocumentosComponentes.as_view(),
        login_url='adesao:login'), name='listar_documentos'),

    # Tela de alteração de upload do plano de trabalho
    path("inserir-documentos/fundo/alterar/<int:pk>", staff_member_required(
        views.AlterarFundoCultura.as_view(),
        login_url='adesao:login'), name='alterar_fundo'),
    path("inserir-documentos/<str:componente>/alterar/<int:pk>", staff_member_required(
        views.AlterarComponente.as_view(),
        login_url='adesao:login'), name='alterar_componente'), 

    # ajax mudança de cadastrador
    url(r'^ajax_cadastrador_cpf$', staff_member_required(views.ajax_cadastrador_cpf), name='ajax_cadastrador_cpf'),


    # Diligência de Componente

    # url(r'^(?P<pk>[0-9]+)/diligencia/(?P<componente>[A-z]+)/(?P<resultado>[0-1])',
    #     staff_member_required(views.DiligenciaComponenteView.as_view()), name="diligencia_componente"),

    path("<int:pk>/diligencia/add", 
        staff_member_required(views.DiligenciaGeralCreateView.as_view()),
        name="diligencia_geral_adicionar"),

    path("<int:pk>/diligencia/<str:componente>", 
        staff_member_required(views.DiligenciaComponenteView.as_view()),
        name="diligencia_componente"),

    path("<int:pk>/diligencia/<str:componente>/<int:pk_componente>/situacao",
        staff_member_required(views.SituacaoArquivoComponenteUpdateView.as_view()),
        name="componente_situacao_atualiza"),

    path("<int:pk>/diligencia", 
        staff_member_required(views.DiligenciaGeralDetailView.as_view()),
        name="diligencia_geral"),

    path("ajax/consultar_cpf",
            staff_member_required(views.ajax_consulta_cpf),
            name="ajax-consulta-cpf"),
    ]