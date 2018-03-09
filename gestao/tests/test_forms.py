import pytest
from django.forms import ModelForm

from gestao.forms import DiligenciaForm
from gestao.models import Diligencia

from ckeditor.widgets import CKEditorWidget


pytestmark = pytest.mark.django_db

def test_existencia_form_diligencia(client):

    """ Testa existência da classe form para a diligência """
    form = DiligenciaForm(resultado='0')
    assert form


def test_campo_texto_diligencia_form(client):
    """
    Testa existência do campo texto_diligência no form referente a diligência
    """
    form = DiligenciaForm(resultado='0')
    assert "<textarea cols=\"40\" id=\"id_texto_diligencia\" name=\"texto_diligencia\" " in form.as_p()


def test_campo_classificao_arquivo_no_form_diligencia(client):
    """ Testa a existência do campo referente a seleção para a classificação do arquivo """

    form = DiligenciaForm(resultado='0')
    assert "<select id=\"id_classificacao_arquivo\" name=\"classificacao_arquivo\"" in form.as_p()


def test_uso_ck_widget_no_texto_diligencia(client):
    """ Testa uso do widget ckeditor para input de texto rich no texto_diligência """

    form = DiligenciaForm(resultado='0')
    assert isinstance(form.fields['texto_diligencia'].widget, CKEditorWidget)


def test_validacao_de_dados_invalidos(client):
    """ Testa se a função is_valid retorna falso para dados inválidos na criação do form """

    data = {'texto_diligencia': 'ta certo, parceiro', 'classificacao_arquivo': 'bla'}

    form = DiligenciaForm(data=data, resultado='0')

    assert not form.is_valid()


def test_tipo_do_form_da_diligencia(client):
    """ Testa se o form da Diligência é do tipo ModelForm """

    assert issubclass(DiligenciaForm, ModelForm)


def test_diligencia_form_usa_model_correta(client):
    """ Testa de a classe DiligenciaForm utiliza a model referente a Diligencia """

    form = DiligenciaForm(resultado='0')

    assert isinstance(form.instance, Diligencia)


def test_fields_form_diligencia(client):
    """Testa as fields dentro do form Diligencia"""

    form = DiligenciaForm(resultado='0')
    fields = ('texto_diligencia', 'classificacao_arquivo')

    assert set(form.Meta.fields).issuperset(set(fields))