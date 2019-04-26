import pytest
from django.forms import ModelForm
from django.shortcuts import reverse

from gestao.forms import DiligenciaComponenteForm, DiligenciaGeralForm
from gestao.forms import CadastradorEnte, DiligenciaForm, AlterarDadosEnte
from gestao.models import DiligenciaSimples
from adesao.models import SistemaCultura

from ckeditor.widgets import CKEditorWidget
from dal.autocomplete import ModelSelect2
from model_mommy import mommy

pytestmark = pytest.mark.django_db


def test_existencia_form_diligencia_componente(client, login, sistema_cultura):
    """ Testa existência da classe form para a diligência de componentes"""

    form = DiligenciaComponenteForm(componente='orgao_gestor', arquivo='arquivo',
        sistema_cultura=sistema_cultura, usuario=login)

    assert form


def test_existencia_form_diligencia_geral(client, login, sistema_cultura):
    """ Testa existência da classe form para a diligência geral"""

    form = DiligenciaGeralForm(sistema_cultura=sistema_cultura, usuario=login)

    assert form


def test_campo_texto_diligencia_form_componente(client, login, sistema_cultura):
    """
    Testa existência do campo texto_diligência no form referente a diligência de componente
    """

    form = DiligenciaComponenteForm(componente='orgao_gestor', arquivo='arquivo',
        sistema_cultura=sistema_cultura, usuario=login)

    assert "<textarea cols=\"40\" id=\"id_texto_diligencia\" name=\"texto_diligencia\" " in form.as_p()


def test_campo_texto_diligencia_form_geral(client, login, sistema_cultura):
    """
    Testa existência do campo texto_diligência no form referente a diligência geral
    """

    form = DiligenciaGeralForm(sistema_cultura=sistema_cultura, usuario=login)

    assert "<textarea cols=\"40\" id=\"id_texto_diligencia\" name=\"texto_diligencia\" " in form.as_p()


def test_campo_classificao_arquivo_no_form_diligencia_componente(client, login, sistema_cultura):
    """ Testa a existência do campo referente a seleção para a classificação do arquivo """

    form = DiligenciaComponenteForm(componente='orgao_gestor', arquivo='arquivo',
        sistema_cultura=sistema_cultura, usuario=login)

    assert "<select name=\"classificacao_arquivo\" id=\"id_classificacao_arquivo\"" in form.as_p()


def test_ausencia_campo_classificao_arquivo_no_form_diligencia_geral(client, login, sistema_cultura):
    """ Testa se o campo referente a seleção para a classificação do arquivo
    não é disonível na diligência geral """

    form = DiligenciaGeralForm(sistema_cultura=sistema_cultura, usuario=login)

    assert "<select name=\"classificacao_arquivo\" id=\"id_classificacao_arquivo\"" not in form.as_p()


def test_uso_ck_widget_no_texto_diligencia_geral(client, login, sistema_cultura):
    """ Testa uso do widget ckeditor para input de texto rich no texto_diligência """

    form = DiligenciaGeralForm(sistema_cultura=sistema_cultura, usuario=login)

    assert isinstance(form.fields['texto_diligencia'].widget, CKEditorWidget)


def test_validacao_de_dados_invalidos(client, login, sistema_cultura):
    """ Testa se a função is_valid retorna falso para dados inválidos na criação do form
    da diligencia de componente"""

    data = {'texto_diligencia': 'ta certo, parceiro', 'classificacao_arquivo': 'bla'}

    form = DiligenciaComponenteForm(data=data, componente='orgao_gestor',
        arquivo="arquivo", sistema_cultura=sistema_cultura, usuario=login)

    assert not form.is_valid()


def test_tipo_do_form_da_diligencia_geral(client):
    """ Testa se o form da diligência geral é do tipo ModelForm """

    assert issubclass(DiligenciaGeralForm, ModelForm)


def test_tipo_do_form_da_diligencia_componente(client):
    """ Testa se o form da diligência de componente é do tipo ModelForm """

    assert issubclass(DiligenciaComponenteForm, ModelForm)


def test_diligencia_form_componente_usa_model_correta(client, login, sistema_cultura):
    """ Testa de a classe DiligenciaForm utiliza a model referente a Diligencia """

    form = DiligenciaComponenteForm(componente='orgao_gestor',
        arquivo='arquivo', sistema_cultura=sistema_cultura, usuario=login)

    assert isinstance(form.instance, DiligenciaSimples)


def test_diligencia_form_geral_usa_model_correta(client, login, sistema_cultura):
    """ Testa de a classe DiligenciaForm utiliza a model referente a Diligencia """

    form = DiligenciaGeralForm(sistema_cultura=sistema_cultura, usuario=login)

    assert isinstance(form.instance, DiligenciaSimples)


def test_fields_form_diligencia_componente(client, login, sistema_cultura):
    """Testa as fields dentro do form de diligencia de componente"""

    form = DiligenciaComponenteForm(componente='orgao_gestor',
        arquivo='arquivo', sistema_cultura=sistema_cultura, usuario=login)

    fields = ('texto_diligencia', 'classificacao_arquivo')

    assert set(form.Meta.fields).issuperset(set(fields))


def test_fields_form_diligencia_geral(client, login, sistema_cultura):
    """Testa as fields dentro do form de diligencia geral"""

    form = DiligenciaGeralForm(sistema_cultura=sistema_cultura, usuario=login)

    fields = ('texto_diligencia',)

    assert set(form.Meta.fields).issuperset(set(fields))


def test_save_alterar_cadastrador_form_com_sistemacultura(sistema_cultura):
    """
    Método save do form CadastradorEnte altera o cadastrador de um sistema
    cultura
    """

    usuario = mommy.make("Usuario", user__username='11416309071')
    data = {'cpf_cadastrador': usuario.user.username}

    form = CadastradorEnte(data=data)
    form.instance = sistema_cultura
    form.is_valid()
    form.save()

    sistema_atualizado = SistemaCultura.sistema.get(
        ente_federado__cod_ibge=sistema_cultura.ente_federado.cod_ibge)

    assert sistema_atualizado.cadastrador == usuario


def test_form_criacao_diligencia_dados_invalidos(sistema_cultura, login):

    data = {'classificacao_arquivo': '3', 'texto_diligencia': ''}

    form = DiligenciaForm(data=data, sistema_cultura=sistema_cultura, usuario=login)

    assert not form.is_valid()


def test_form_criacao_diligencia_dados_validos(sistema_cultura, login):

    data = {'classificacao_arquivo': '2'}

    form = DiligenciaForm(data=data, sistema_cultura=sistema_cultura, usuario=login)

    assert form.is_valid()


def test_form_alterar_dados_ente_validos(sistema_cultura, login):

    data = {'estado_processo': '3'}

    form = AlterarDadosEnte(data=data)

    assert form.is_valid()
