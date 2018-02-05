import pytest

from django.template import Context, Template, Engine
from django.template.base import TemplateDoesNotExist

pytestmark = pytest.mark.django_db


@pytest.fixture
def engine():
    """ Configura a engine de Templates do Django """

    engine = Engine.get_default()

    return engine

def test_existencia_template_diligencia(engine, client):
    """ Testando existência do template para criação da diligência"""

    try:
        template = engine.get_template(template_name='gestao/diligencia/diligencia.html', dirs=engine.dirs)
    except TemplateDoesNotExist:
        template = ''

    assert isinstance(template, Template)


def test_botoes_acao_diligencia_template(engine, client):
    """Testa existencia dos botões de enviar e cancelar
    no template de diligência"""

    template = engine.get_template(
        template_name='gestao/diligencia/diligencia.html', dirs=engine.dirs)
    rendered_template = template.render(Context({}))

    # __import__('ipdb').set_trace()
    assert "<button class='btn btn-primary'>Enviar</button>" in rendered_template
    assert "<button class='btn btn-secondary'>Cancelar</button>" in rendered_template


def test_gestao_template(engine, client):
    """Testa se o template da gestão está sendo carregado"""

    template = engine.get_template(
        template_name='gestao/diligencia/diligencia.html', dirs=engine.dirs)

    rendered_template = template.render(Context({}))

    assert "<!DOCTYPE html>" in rendered_template


def test_informacoes_arquivo_enviado(engine, client):
    """Testa se o template exibe as informações do arquivo enviado"""

    template = engine.get_template(
        template_name='gestao/diligencia/diligencia.html', dirs=engine.dirs
    )
    context = Context({'nome_arquivo': 'lei_sistema_para.pdf', 'data_envio': '10/08/2017', 'ente_federado': 'Pará'})
    rendered_template = template.render(context)

    # import ipdb; ipdb.set_trace()
    
    assert context['nome_arquivo'] in rendered_template
    assert context['data_envio'] in rendered_template
    assert context['ente_federado'] in rendered_template
