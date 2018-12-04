import pytest

from django.template import Context
from django.template import Engine
from django.template import Template
from django.template import TemplateDoesNotExist
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from planotrabalho.models import PlanoTrabalho
from gestao.forms import DiligenciaForm, DiligenciaComponenteForm
from gestao.models import Diligencia
from adesao.models import SistemaCultura

from model_mommy import mommy

pytestmark = pytest.mark.django_db


@pytest.fixture
def context(login):
    """ Retorna um contexto básico necessário para rendereziar o template de diligência """

    context = Context({'usuario_id': login.id})
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

    template = engine.get_template(template_name='diligencia.html')

    return template


def test_existencia_template_diligencia(engine, client):
    """ Testando existência do template para criação da diligência"""

    try:
        template = engine.get_template(template_name='diligencia.html')
    except TemplateDoesNotExist:
        template = ''

    assert isinstance(template, Template)


def test_retorno_do_botao_cancelar_de_diligencia(client, template, context, sistema_cultura):
    """ Testa se o botão cancelar presente na página de diligência
    retorna para a página de detalhe do município correspondente"""

    context['sistema_cultura'] = sistema_cultura

    rendered_template = template.render(context)

    url = reverse('gestao:detalhar', kwargs={"cod_ibge": sistema_cultura.ente_federado.cod_ibge})
    html = "<a href=\"{url}\" class=\"btn btn-danger\">Cancelar</a>".format(url=url)

    assert html in rendered_template


def test_botao_acao_enviar_diligencia_template(template, client, context, sistema_cultura):
    """Testa existencia dos botão de enviar no template de diligência"""

    context['sistema_cultura'] = sistema_cultura
    rendered_template = template.render(context)

    assert "<input class=\"btn btn-primary\" type=\"submit\"></input>" in rendered_template


def test_gestao_template(template, client, context, sistema_cultura):
    """Testa se o template da gestão está sendo carregado"""

    context['sistema_cultura'] = sistema_cultura
    rendered_template = template.render(context)

    assert "<!DOCTYPE html>" in rendered_template


def test_informacoes_arquivo_enviado(template, client, context, sistema_cultura):
    """Testa se o template exibe as informações do arquivo enviado"""

    context['ente_federado'] = 'Pará'
    context['sistema_cultura'] = sistema_cultura

    rendered_template = template.render(context)

    assert context['ente_federado'] in rendered_template


def test_opcoes_de_classificacao_da_diligencia(template, client, context, login, sistema_cultura):
    """Testa se a Classificação(Motivo) apresenta as opções conforme a especificação."""

    opcoes = ("Arquivo danificado",
              "Arquivo incompleto",
              "Arquivo incorreto"
              )

    form = DiligenciaComponenteForm(componente='orgao_gestor', usuario=login,
        sistema_cultura=sistema_cultura)
    context['form'] = form
    context['sistema_cultura'] = sistema_cultura
    context['componente'] = mommy.make("Componente")
    rendered_template = template.render(context)

    assert opcoes[0] in rendered_template
    assert opcoes[1] in rendered_template
    assert opcoes[2] in rendered_template


def test_opcoes_em_um_dropdown(template, client, context, login, sistema_cultura):
    """Testa se as Classificações(Motivo) estão presentes dentro de um dropdown."""
    opcoes = [
            {"description": "Arquivo danificado", "value": "4"},
            {"description": "Arquivo incompleto", "value": "5"},
            {"description": "Arquivo incorreto", "value": "6"}
    ]

    form = DiligenciaComponenteForm(componente='orgao_gestor', usuario=login,
        sistema_cultura=sistema_cultura)
    context['form'] = form
    context['sistema_cultura'] = sistema_cultura
    context['componente'] = mommy.make("Componente")
    rendered_template = template.render(context)

    assert "<select name=\"classificacao_arquivo\" id=\"id_classificacao_arquivo\">" in rendered_template
    for opcao in opcoes:
        assert "<option value=\"{value}\">{description}</option>".format(value=opcao['value'], description=opcao['description'])
    assert "</select>" in rendered_template


@pytest.mark.skip
def test_informacoes_do_historico_de_diligecias_do_componente(template, client, context, sistema_cultura):
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
    context['sistema_cultura'] = sistema_cultura
    rendered_template = template.render(context)

    for diligencia in diligencias:
        assert diligencia['usuario']["nome_usuario"] in rendered_template
        assert diligencia['classificacao_arquivo']['descricao'] in rendered_template
        assert diligencia['data_criacao'] in rendered_template
        assert diligencia['texto_diligencia'] in rendered_template


def test_formatacao_individual_das_diligencias_no_historico(template, client, context, sistema_cultura):
    """Testa a formatacao de cada uma das diligências dentro do bloco de Histórico de Diligências."""

    diligencias = [
        {"usuario": {"nome_usuario": "Jaozin Silva" }, "data_criacao": "10/08/2018", 
            "texto_diligencia": "Arquivo danificado, corrompido"},

        {"usuario": {"nome_usuario": "Pedrin Silva" }, "data_criacao": "10/08/2018", 
            "texto_diligencia": "Arquivo incompleto, informações faltando"},

        {"usuario": {"nome_usuario": "Luizin Silva" }, "data_criacao": "10/08/2018", 
            "texto_diligencia": "Arquivo com informações incorretas"}
    ]

    context['historico_diligencias'] = diligencias
    context['sistema_cultura'] = sistema_cultura
    rendered_template = template.render(context)
    for diligencia in diligencias:

        assert "<li class=\"list-group-item\" style=\"border: 1px solid #b3b5b6\"><b>Usuário:</b> {nome}</li>".format(nome=diligencia['usuario']["nome_usuario"]) in rendered_template
        assert "<li class=\"list-group-item\" style=\"border: 1px solid #b3b5b6\"><b>Data:</b> {data}</li>".format(data=diligencia['data_criacao']) in rendered_template
        assert "<li class=\"list-group-item\" style=\"border: 1px solid #b3b5b6\"><b>Resumo:</b> {resumo}</li>".format(resumo=diligencia["texto_diligencia"]) in rendered_template


def test_renderizacao_js_form_diligencia(template, client, context, sistema_cultura, login):
    """Testa se o javascript do form está sendo renderizado corretamente"""

    form = DiligenciaForm(sistema_cultura=sistema_cultura, usuario=login)

    context['form'] = form
    context['sistema_cultura'] = sistema_cultura

    rendered_template = template.render(context)

    assert "<script type=\"text/javascript\" src=\"/static/ckeditor/ckeditor/ckeditor.js\">" in rendered_template


def test_opcoes_de_avaliacao_documentos_plano_de_trabalho(client, login_staff, sistema_cultura):
    """ Testa se há a opção de avaliar negativamente e positivamente um
    documento enviado do Plano Trabalho """

    componentes = (
        'orgao_gestor',
        'fundo_cultura',
        'legislacao',
        'conselho',
        'plano'
    )

    legislacao = mommy.make("Componente", tipo=0, situacao=1)
    arquivo = SimpleUploadedFile("lei.txt", b"file_content", content_type="text/plain")
    diligencia = mommy.make("DiligenciaSimples")
    orgao_gestor = mommy.make("Componente", tipo=1, situacao=1)
    fundo = mommy.make("FundoDeCultura", tipo=2, situacao=1)
    conselho = mommy.make("Componente", tipo=3, situacao=1)
    plano = mommy.make("Componente", tipo=4, situacao=1)

    sistema_cultura.legislacao = legislacao
    sistema_cultura.orgao_gestor = orgao_gestor
    sistema_cultura.fundo_cultura = fundo
    sistema_cultura.conselho = conselho
    sistema_cultura.plano = plano
    sistema_cultura.estado_processo = '6'
    sistema_cultura.save()

    orgao_gestor.arquivo = arquivo
    orgao_gestor.diligencia = diligencia
    orgao_gestor.save()

    legislacao.arquivo = arquivo
    legislacao.diligencia = diligencia
    legislacao.save()

    conselho.arquivo = arquivo
    conselho.diligencia = diligencia
    conselho.save()

    fundo.arquivo = arquivo
    fundo.diligencia = diligencia
    fundo.save()

    plano.arquivo = arquivo
    plano.diligencia = diligencia
    plano.save()

    request = client.get(f"/gestao/ente/{sistema_cultura.ente_federado.cod_ibge}")

    for componente in componentes:
        assert '<a href=\"/gestao/{}/diligencia/{}">'.format(sistema_cultura.id, componente) in request.rendered_content


def test_informacoes_diligencia_componente(client, login_staff, sistema_cultura):
    """
    Testa se a linha de download do arquivo é renderizada, visto que
    só deve ser renderizada quando a diligência é por componente
    """

    orgao_gestor = mommy.make("Componente", tipo=1, situacao=1)
    sistema_cultura.orgao_gestor = orgao_gestor
    sistema_cultura.save()

    arquivo = SimpleUploadedFile("lei.txt", b"file_content", content_type="text/plain")
    orgao_gestor.arquivo = arquivo
    orgao_gestor.save()

    request = client.get('/gestao/{}/diligencia/{}'.format(
        sistema_cultura.id, "orgao_gestor"))

    assert "<h2>Informações sobre o Arquivo Enviado</h2>" in request.rendered_content
    assert "<b>Download do arquivo</b>" in request.rendered_content


def test_informacoes_diligencia_geral(client, login_staff, sistema_cultura):
    """
    Testa se linha de informações sobre o Plano Trabalho é renderizada,
    visto que só deve ser renderizada quando a diligência é geral.
    """

    url = reverse('gestao:diligencia_geral_adicionar', kwargs={"pk": sistema_cultura.id})
    request = client.get(url)


    assert "<h2>Informações sobre o Plano Trabalho</h2>" in request.rendered_content