import pytest

from django.template import Context, Template, Engine
from django.template.base import TemplateDoesNotExist

pytestmark = pytest.mark.django_db


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


def test_botoes_acao_diligencia_template(template, client):
    """Testa existencia dos botões de enviar e cancelar
    no template de diligência"""

    rendered_template = template.render(Context({}))

    # __import__('ipdb').set_trace()
    assert "<button class='btn btn-primary'>Enviar</button>" in rendered_template
    assert "<button class='btn btn-secondary'>Cancelar</button>" in rendered_template


def test_gestao_template(template, client):
    """Testa se o template da gestão está sendo carregado"""

    rendered_template = template.render(Context({}))

    assert "<!DOCTYPE html>" in rendered_template


def test_informacoes_arquivo_enviado(template, client):
    """Testa se o template exibe as informações do arquivo enviado"""

    context = Context({'nome_arquivo': 'lei_sistema_para.pdf', 'data_envio': '10/08/2017', 'ente_federado': 'Pará'})
    rendered_template = template.render(context)

    # import ipdb; ipdb.set_trace()
    
    assert context['nome_arquivo'] in rendered_template
    assert context['data_envio'] in rendered_template
    assert context['ente_federado'] in rendered_template


def test_titulo_bloco_informacoes_arquivo(template, client):
    """Testa se o título Informações sobre o Arquivo Enviado está dentre de uma tag de título h2"""

    rendered_template = template.render(Context({}))

    assert "<h2>Informações sobre o Arquivo Enviado</h2>" in rendered_template


def test_formatacao_informacoes_sobre_arquivo_enviado(template, client):
    """Testa se cada informação sobre o arquivo enviado está formatada com a tag <p>"""

    context = Context({'nome_arquivo': 'lei_sistema_para.pdf', 'data_envio': '10/08/2017', 'ente_federado': 'Pará'})
    rendered_template = template.render(context)

    assert "<p>{}</p>".format(context['nome_arquivo']) in rendered_template
    assert "<p>{}</p>".format(context['data_envio']) in rendered_template
    assert "<p>{}</p>".format(context['ente_federado']) in rendered_template


def test_opcoes_de_classificacao_da_diligencia(template, client):
    """Testa se a Classificação(Motivo) apresenta as opções conforme a especificação."""

    opcoes = [
        {"description": "Arquivo Danificado", "value": "arquivo_danificado"},
        {"description": "Arquivo Incompleto", "value": "arquivo_incompleto"},
        {"description": "Arquivo Incorreto", "value": "arquivo_incorreto"}
    ]
    
    context = Context({"classificacoes": opcoes})
    rendered_template = template.render(context)

    assert opcoes[0]['description'] in rendered_template
    assert opcoes[1]['description'] in rendered_template
    assert opcoes[2]['description'] in rendered_template


def test_opcoes_em_um_dropdown(template, client):
    """Testa se as Classificações(Motivo) estão presentes dentro de um dropdown."""

    opcoes = [
        {"description": "Arquivo Danificado", "value": "arquivo_danificado"},
        {"description": "Arquivo Incompleto", "value": "arquivo_incompleto"},
        {"description": "Arquivo Incorreto", "value": "arquivo_incorreto"}
    ]
    
    context = Context({"classificacoes": opcoes})
    rendered_template = template.render(context)

    assert "<select>" in rendered_template
    for opcao in opcoes:
        assert "<option value=\"{value}\">{description}</option>".format(value=opcao['value'], description=opcao['description'])
    assert "</select>" in rendered_template


def test_informacoes_do_historico_de_diligecias_do_componente(template, client):
    """ Testa informações referente ao histórico de diligências do componente. """

    diligencias = [
        {"nome_usuario": "Jaozin Silva", "motivo": "Arquivo Danificado", 
            "data": "10/08/2018", "resumo": "Arquivo danificado, corrompido"},

        {"nome_usuario": "Pedrin Silva", "motivo": "Arquivo Incompleto", 
            "data": "10/08/2018", "resumo": "Arquivo incompleto, informações faltando"},
        
        {"nome_usuario": "Luizin Silva", "motivo": "Arquivo Incorreto", 
            "data": "10/08/2018", "resumo": "Arquivo com informações incorretas"}
    ]

    context = Context({"historico_diligencias": diligencias})
    rendered_template = template.render(context)

    for diligencia in diligencias:
        assert diligencia['nome_usuario'] in rendered_template
        assert diligencia['motivo'] in rendered_template
        assert diligencia['data'] in rendered_template
        assert diligencia['resumo'] in rendered_template


def test_formatacao_historico_de_diligencias(template,client):
    """Testa a formatação do bloco de histórico de diligências em uma tag dev"""

    rendered_template = template.render(Context({}))
    
    assert "<div class=\"historico_diligencias\">" in rendered_template

def test_formatacao_individual_das_diligencias_no_historico(template, client):
    """Testa a formatacao de cada uma das diligências dentro do bloco de Histórico de Diligências."""

    diligencias = [
        {"nome_usuario": "Jaozin Silva", "motivo": "Arquivo Danificado", 
            "data": "10/08/2018", "resumo": "Arquivo danificado, corrompido"},

        {"nome_usuario": "Pedrin Silva", "motivo": "Arquivo Incompleto", 
            "data": "10/08/2018", "resumo": "Arquivo incompleto, informações faltando"},
        
        {"nome_usuario": "Luizin Silva", "motivo": "Arquivo Incorreto", 
            "data": "10/08/2018", "resumo": "Arquivo com informações incorretas"}
    ]

    context = Context({"historico_diligencias": diligencias})
    rendered_template = template.render(context)

    for diligencia in diligencias:
        assert "<div>Usuário: {nome}, Motivo: {motivo}, Data: {data}, Resumo: {resumo}</div>".format(
                                                                nome=diligencia['nome_usuario'],
                                                                motivo=diligencia['motivo'],
                                                                data=diligencia['data'],
                                                                resumo=diligencia['resumo']) in rendered_template


def test_existencia_campo_texto_diligencia(template, client):
    """Testa se há uma campo de texto para inserção da diligência na página de diligência"""

    rendered_template = template.render(Context({}))

    assert "<div id=\"campo_texto\"></div>" in rendered_template