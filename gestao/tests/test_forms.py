import pytest

from gestao.forms import DiligenciaForm

pytestmark = pytest.mark.django_db

def test_existencia_form_diligencia(client):
    """ Testa existência da classe form para a diligência """
    form = DiligenciaForm()
    assert form


def test_campo_texto_diligencia_form(client):
    """ 
    Testa existência do campo texto_diligência no form referente a diligência 
    """
    form = DiligenciaForm()
    assert "<input id=\"id_texto_diligencia\" name=\"texto_diligencia\" type=\"text\" " in form.as_p()


def test_campo_classificao_arquivo_no_form_diligencia(client):
    """ Testa a existência do campo referente a seleção para a classificação do arquivo """

    form = DiligenciaForm()
    assert "<select id=\"id_classificacao_arquivo\" name=\"classificacao_arquivo\"" in form.as_p()