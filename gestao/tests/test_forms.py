import pytest

from gestao.forms import DiligenciaForm

from ckeditor.widgets import CKEditorWidget


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
    assert "<textarea cols=\"40\" id=\"id_texto_diligencia\" name=\"texto_diligencia\" " in form.as_p()
    


def test_campo_classificao_arquivo_no_form_diligencia(client):
    """ Testa a existência do campo referente a seleção para a classificação do arquivo """

    form = DiligenciaForm()
    assert "<select id=\"id_classificacao_arquivo\" name=\"classificacao_arquivo\"" in form.as_p()


def test_uso_ck_widget_no_texto_diligencia(client):
    """ Testa uso do widget ckeditor para input de texto rich no texto_diligência """

    form = DiligenciaForm()
    assert isinstance(form.fields['texto_diligencia'].widget, CKEditorWidget)


def test_validacao_de_dados_invalidos(client):
    """ Testa se a função is_valid retorna falso para dados inválidos na criação do form """

    data = {'texto_diligencia': 'ta certo, parceiro', 'classificacao_arquivo': 'bla'}

    form = DiligenciaForm(data)

    assert not form.is_valid()