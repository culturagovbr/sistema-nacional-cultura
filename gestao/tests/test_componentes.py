import pytest

from django.template import Context, Template, Engine
from django.template.base import TemplateDoesNotExist

pytestmark = pytest.mark.django_db

def test_existencia_template_diligencia(client):
    """ Testando existência do template para criação da diligência"""

    engine = Engine.get_default()
    try:
        template = engine.get_template(template_name='gestao/diligencia/diligencia.html', dirs=engine.dirs)
    except TemplateDoesNotExist:
        template = ''

    assert isinstance(template, Template)
    
def test_botoes_acao_diligencia_template(client):
    """Testa existencia dos botões de enviar e cancelar no template de diligência"""

    engine = Engine.get_default()

    template = engine.get_template(template_name='gestao/diligencia/diligencia.html', dirs=engine.dirs)
    rendered_template = template.render(Context())

    # self.assetInHTML("btn-primary" ", rendered_template)
    assert "<button class='btn btn-primary'>Enviar</button>" in rendered_template
    assert "<button class='btn btn-secondary'>Cancelar</button>" in rendered_template

def test_gestao_template(client):
    """Testa se o template da gestão está sendo carregado"""

    engine = Engine.get_default()

    template = engine.get_template(template_name='gestao/diligencia/diligencia.html', dirs=engine.dirs)

    assert template.nodelist[0] in 'gestao/base_gestao.html'
