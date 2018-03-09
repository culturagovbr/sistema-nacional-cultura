import pytest

from django.template import Context, Template, Engine
from django.template.base import TemplateDoesNotExist
from django.core.urlresolvers import reverse

from planotrabalho.models import SituacoesArquivoPlano
from gestao.forms import DiligenciaForm

from test_views import login
from test_views import login_staff
from test_views import plano_trabalho

pytestmark = pytest.mark.django_db


@pytest.fixture
def situacoes():
    """Cria situações dos arquivos do Plano Trabalho enviados no banco de testes"""
    situacoes = (
        (0, 'Em preenchimento'),
        (1, 'Avaliando anexo'),
        (2, 'Concluída'),
        (3, 'Arquivo aprovado com ressalvas'),
        (4, 'Arquivo danificado'),
        (5, 'Arquivo incompleto'),
        (6, 'Arquivo incorreto')
    )

    for situacao in situacoes:
        SituacoesArquivoPlano.objects.create(id=situacao[0], descricao=situacao[1])

    return SituacoesArquivoPlano.objects.all()


@pytest.fixture
def usuario(plano_trabalho):
    """ Retorna um usuario associado a um
    plano de trabalho e um ente_federado """

    return plano_trabalho.usuario

@pytest.fixture
def context(usuario):
    """ Retorna um contexto básico necessário para rendereziar o template de diligência """

    context = Context({'usuario_id': usuario.id})
    return context


@pytest.fixture
def engine():
    """ Configura a engine de Templates do Django """

    engine = Engine.get_default()

    return engine


@pytest.fixture
def template(engine):
    """ Injeta o template 'gestao/diligencia/diligencia.html' como um objeto Template
        pronto para ser usado."""

    template = engine.get_template(template_name='gestao/diligencia/diligencia.html', dirs=engine.dirs)

    return template


def test_existencia_template_diligencia(engine, client):
    """ Testando existência do template para criação da diligência"""

    try:
        template = engine.get_template(template_name='gestao/diligencia/diligencia.html', dirs=engine.dirs)
    except TemplateDoesNotExist:
        template = ''

    assert isinstance(template, Template)


def test_retorno_do_botao_cancelar_de_diligencia(client, template, context, usuario):
    """ Testa se o botão cancelar presente na página de diligência
    retorna para a página de detalhe do município correspondente"""

    rendered_template = template.render(context)

    url_detalhar = reverse('gestao:detalhar', args=[usuario.id])
    html_cancelar = "<a href=\"{url_detalhar}\" class=\"btn btn-danger\">Cancelar</a>".format(url_detalhar=url_detalhar)

    assert html_cancelar in rendered_template


def test_botao_acao_enviar_diligencia_template(template, client, context):
    """Testa existencia dos botão de enviar
    no template de diligência"""

    rendered_template = template.render(context)

    assert "<input class=\"btn btn-primary\" type=\"submit\"></input>" in rendered_template


def test_gestao_template(template, client, context):
    """Testa se o template da gestão está sendo carregado"""

    rendered_template = template.render(context)

    assert "<!DOCTYPE html>" in rendered_template


def test_informacoes_arquivo_enviado(template, client, context):
    """Testa se o template exibe as informações do arquivo enviado"""

    context['data_envio'] = '10/08/2017'
    context['ente_federado'] = 'Pará'

    rendered_template = template.render(context)

    assert context['data_envio'] in rendered_template
    assert context['ente_federado'] in rendered_template


def test_titulo_bloco_informacoes_arquivo(template, client, context):
    """Testa se o título Informações sobre o Arquivo Enviado está dentre de uma tag de título h2"""

    rendered_template = template.render(context)

    assert "<h2>Informações sobre o Arquivo Enviado</h2>" in rendered_template


def test_formatacao_informacoes_sobre_arquivo_enviado(template, client, context):
    """Testa se cada informação sobre o arquivo enviado está formatada com a tag <p>"""

    context['nome_arquivo'] = 'lei_sistema_para.pdf'
    context['data_envio'] = '10/08/2017'
    context['ente_federado'] = 'Pará'
    rendered_template = template.render(context)

    assert "<a href = > <b>Download do arquivo</b></a>" in rendered_template
    assert "<p><b>Data de Envio do Arquivo:</b> {}</p>".format(context['data_envio']) in rendered_template
    assert "<p><b>Ente Federado:</b> {}</p>".format(context['ente_federado']) in rendered_template


def test_opcoes_de_classificacao_da_diligencia(template, client, situacoes, context):
    """Testa se a Classificação(Motivo) apresenta as opções conforme a especificação."""

    opcoes = ("Arquivo danificado",
              "Arquivo incompleto",
              "Arquivo incorreto"
              )

    form = DiligenciaForm(resultado='0')
    context['form'] = form
    rendered_template = template.render(context)

    assert opcoes[0] in rendered_template
    assert opcoes[1] in rendered_template
    assert opcoes[2] in rendered_template


def test_opcoes_em_um_dropdown(template, client, context):
    """Testa se as Classificações(Motivo) estão presentes dentro de um dropdown."""
    opcoes = [
            {"description": "Arquivo Danificado", "value": "4"},
            {"description": "Arquivo Incompleto", "value": "5"},
            {"description": "Arquivo Incorreto", "value": "6"}
    ]

    form = DiligenciaForm(resultado='0')
    context['form'] = form
    rendered_template = template.render(context)

    assert "<select id=\"id_classificacao_arquivo\" name=\"classificacao_arquivo\">" in rendered_template
    for opcao in opcoes:
        assert "<option value=\"{value}\">{description}</option>".format(value=opcao['value'], description=opcao['description'])
    assert "</select>" in rendered_template


def test_informacoes_do_historico_de_diligecias_do_componente(template, client, context):
    """ Testa informações referente ao histórico de diligências do componente. """

    diligencias = [
        {"usuario": {"nome_usuario": "Jaozin Silva" }, "classificacao_arquivo": {"descricao": "Arquivo Danificado"},
            "data_criacao": "10/08/2018", "texto_diligencia": "Arquivo danificado, corrompido"},

        {"usuario": {"nome_usuario": "Pedrin Silva" }, "classificacao_arquivo": {"descricao": "Arquivo incompleto"},
            "data_criacao": "10/08/2018", "texto_diligencia": "Arquivo incompleto, informações faltando"},

        {"usuario": {"nome_usuario": "Luizin Silva" }, "classificacao_arquivo": {"descricao": "Arquivo incorreto"},
            "data_criacao": "10/08/2018", "texto_diligencia": "Arquivo com informações incorretas"}
    ]

    context['historico_diligencias'] = diligencias
    rendered_template = template.render(context)

    for diligencia in diligencias:
        assert diligencia['usuario']["nome_usuario"] in rendered_template
        assert diligencia['classificacao_arquivo']['descricao'] in rendered_template
        assert diligencia['data_criacao'] in rendered_template
        assert diligencia['texto_diligencia'] in rendered_template


def test_formatacao_individual_das_diligencias_no_historico(template, client, context):
    """Testa a formatacao de cada uma das diligências dentro do bloco de Histórico de Diligências."""

    diligencias = [
        {"usuario": {"nome_usuario": "Jaozin Silva" }, "classificacao_arquivo": {"descricao": "Arquivo Danificado"},
            "data_criacao": "10/08/2018", "texto_diligencia": "Arquivo danificado, corrompido"},

        {"usuario": {"nome_usuario": "Pedrin Silva" }, "classificacao_arquivo": {"descricao": "Arquivo incompleto"},
            "data_criacao": "10/08/2018", "texto_diligencia": "Arquivo incompleto, informações faltando"},

        {"usuario": {"nome_usuario": "Luizin Silva" }, "classificacao_arquivo": {"descricao": "Arquivo incorreto"},
            "data_criacao": "10/08/2018", "texto_diligencia": "Arquivo com informações incorretas"}
    ]

    context['historico_diligencias'] = diligencias
    rendered_template = template.render(context)
    for diligencia in diligencias:
        
        assert "<li class=\"list-group-item\" style=\"border: 1px solid #b3b5b6\"><b>Usuário:</b> {nome}</li>".format(nome=diligencia['usuario']["nome_usuario"]) in rendered_template
        assert "<li class=\"list-group-item\" style=\"border: 1px solid #b3b5b6\"><b>Motivo:</b> {motivo}</li>".format(motivo=diligencia['classificacao_arquivo']["descricao"]) in rendered_template
        assert "<li class=\"list-group-item\" style=\"border: 1px solid #b3b5b6\"><b>Data:</b> {data}</li>".format(data=diligencia['data_criacao']) in rendered_template
        assert "<li class=\"list-group-item\" style=\"border: 1px solid #b3b5b6\"><b>Resumo:</b> {resumo}</li>".format(resumo=diligencia["texto_diligencia"]) in rendered_template
        
          


def test_renderizacao_js_form_diligencia(template, client, context):
    """Testa se o javascript do form está sendo renderizado corretamente"""
    form = DiligenciaForm(resultado='0')

    context['form'] = form
    rendered_template = template.render(context)

    assert "<script type=\"text/javascript\" src=\"/static/ckeditor/ckeditor/ckeditor.js\">" in rendered_template


def test_opcao_avaliacao_negativa_documentos_plano_de_trabalho(client, plano_trabalho, login_staff):
    """ Testa se há a opção de avaliar negativamente um documento enviado do Plano Trabalho """

    componentes = (
        'orgao_gestor',
        'plano_cultura',
        'fundo_cultura',
        'criacao_sistema',
        'conselho_cultural',
    )

    usuario = plano_trabalho.usuario
    usuario.estado_processo = '6'
    usuario.save()

    request = client.get('/gestao/detalhar/municipio/{}'.format(usuario.id))

    for componente in componentes:
        assert '<a href=\"/gestao/{}/diligencia/{}/{}\">'.format(plano_trabalho.id, componente, "0") in request.rendered_content


def test_opcao_avaliacao_positiva_documentos_plano_de_trabalho(client, plano_trabalho, login_staff):

    componentes = (
        'orgao_gestor',
        'plano_cultura',
        'fundo_cultura',
        'criacao_sistema',
        'conselho_cultural',
    )

    usuario = plano_trabalho.usuario
    usuario.estado_processo = '6'
    usuario.save()

    request = client.get('/gestao/detalhar/municipio/{}'.format(usuario.id))

    for componente in componentes:
        assert '<a href=\"/gestao/{}/diligencia/{}/{}\">'.format(plano_trabalho.id, componente, "1") in request.rendered_content

