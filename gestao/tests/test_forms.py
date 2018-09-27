import pytest
from django.forms import ModelForm
from django.shortcuts import reverse

from gestao.forms import DiligenciaForm
from gestao.models import Diligencia

from ckeditor.widgets import CKEditorWidget
from dal.autocomplete import ModelSelect2
from model_mommy import mommy

from gestao.forms import AlterarCadastradorForm

pytestmark = pytest.mark.django_db


@pytest.mark.skip()
def test_existencia_form_diligencia(client):

    """ Testa existência da classe form para a diligência """
    form = DiligenciaForm(resultado='0', componente='1')
    assert form


@pytest.mark.skip()
def test_campo_texto_diligencia_form(client):
    """
    Testa existência do campo texto_diligência no form referente a diligência
    """
    form = DiligenciaForm(resultado='0', componente='1')
    assert "<textarea cols=\"40\" id=\"id_texto_diligencia\" name=\"texto_diligencia\" " in form.as_p()


@pytest.mark.skip()
def test_campo_classificao_arquivo_no_form_diligencia(client):
    """ Testa a existência do campo referente a seleção para a classificação do arquivo """

    form = DiligenciaForm(resultado='0', componente='1')
    assert "<select name=\"classificacao_arquivo\" id=\"id_classificacao_arquivo\"" in form.as_p()


@pytest.mark.skip()
def test_uso_ck_widget_no_texto_diligencia(client):
    """ Testa uso do widget ckeditor para input de texto rich no texto_diligência """

    form = DiligenciaForm(resultado='0', componente='1')
    assert isinstance(form.fields['texto_diligencia'].widget, CKEditorWidget)


@pytest.mark.skip()
def test_validacao_de_dados_invalidos(client):
    """ Testa se a função is_valid retorna falso para dados inválidos na criação do form """

    data = {'texto_diligencia': 'ta certo, parceiro', 'classificacao_arquivo': 'bla'}

    form = DiligenciaForm(data=data, resultado='0', componente='1')

    assert not form.is_valid()


def test_tipo_do_form_da_diligencia(client):
    """ Testa se o form da Diligência é do tipo ModelForm """

    assert issubclass(DiligenciaForm, ModelForm)


@pytest.mark.skip()
def test_diligencia_form_usa_model_correta(client):
    """ Testa de a classe DiligenciaForm utiliza a model referente a Diligencia """

    form = DiligenciaForm(resultado='0', componente='1')

    assert isinstance(form.instance, Diligencia)

@pytest.mark.skip()
def test_fields_form_diligencia(client):
    """Testa as fields dentro do form Diligencia"""

    form = DiligenciaForm(resultado='0', componente='1')
    fields = ('texto_diligencia', 'classificacao_arquivo')

    assert set(form.Meta.fields).issuperset(set(fields))


@pytest.mark.xfail(strict=True)
def test_form_altera_cadastrador(client):
    """
    Testa a existencia de um formulário para alterar o cadastrador de uma
    adesão.
    """

    with pytest.raises(ImportError) as exception:
        from gestao.forms import AlterarCadastradorForm


def test_campos_form_altera_cadastrador(client):
    """
    Testa a presença dos campos "CPF", "uf", e "Municipio" no formulário para
    alterar o cadastrador de uma adesão.
    """

    form = AlterarCadastradorForm()
    fields = ("cpf_usuario", "estado", "municipio", "data_publicacao_acordo")

    assert set(form.Meta.fields) == set(fields)


def test_widget_estado_form_alterar_cadastrador(client):
    """
    Testa o uso do widget ModelSelect2 na campo estado no form de
    alterar cadastrador
    """

    form = AlterarCadastradorForm()
    assert isinstance(form['estado'].field.widget, ModelSelect2)


def test_url_widget_estado_form_alterar_cadastrador(client):
    """
    Testa url usada pelo widget ModelSelect2 no campo estado no form
    de alterar cadastrador
    """

    form = AlterarCadastradorForm()
    uf_url = reverse('gestao:uf_chain')

    assert form['estado'].field.widget.url == uf_url


def test_widget_municipio_form_alterar_cadastrador(client):
    """
    Testa o uso do widget ModelSelect2 no campo municipio no form de
    alterar cadastrador
    """

    form = AlterarCadastradorForm()
    assert isinstance(form['municipio'].field.widget, ModelSelect2)


def test_url_widget_municipio_form_alterar_cadastrador(client):
    """
    Testa url usada pelo widget ModelSelect2 no campo municipio no
    form de alterar cadastrador
    """

    form = AlterarCadastradorForm()
    municipio_url = reverse('gestao:cidade_chain')
    assert form['municipio'].field.widget.url == municipio_url


def test_save_alterar_cadastrador_form_com_sistemacultura(plano_trabalho):
    """
    Método save do form AlterarCadastradorForm altera as informações necessárias,
    quando um ente fedarado já possui um SistemaCultura associado
    """
    cidade = mommy.make('Cidade')
    municipio = mommy.make('Municipio', cidade=cidade, estado=cidade.uf)
    user = mommy.make('Usuario', municipio=municipio)
    new_user = mommy.make('Usuario', user__username='23012616039')

    mommy.make('SistemaCultura', cadastrador=user, uf=municipio.estado,
               cidade=municipio.cidade)
    data = {'cpf_usuario': new_user.user.username,
            'estado': municipio.estado.codigo_ibge,
            'municipio': municipio.cidade.id}
    form = AlterarCadastradorForm(data=data)
    form.is_valid()
    form.save()

    municipio.refresh_from_db()

    assert municipio.usuario == new_user


def test_save_alterar_cadastrador_form_sem_sistemacultura(plano_trabalho):
    """
    Método save do form AlterarCadastradorForm altera as informações necessárias,
    quando um ente fedarado NÂO possui um SistemaCultura associado
    """
    cidade = mommy.make('Cidade')
    municipio = mommy.make('Municipio', cidade=cidade, estado=cidade.uf)
    mommy.make('Usuario', municipio=municipio)
    new_user = mommy.make('Usuario', user__username='23012616039')

    data = {'cpf_usuario': new_user.user.username,
            'estado': municipio.estado.codigo_ibge,
            'municipio': municipio.cidade.id}
    form = AlterarCadastradorForm(data=data)
    form.is_valid()
    form.save()

    municipio.refresh_from_db()

    assert municipio.usuario == new_user


def test_save_alterar_cadastrador_form_sem_municipio(plano_trabalho):
    """
    Testa form de alteração de cadastrador no caso que não existe municipío
    """

    estado = mommy.make('Uf')
    cidade = mommy.make('Cidade', uf=estado)
    new_user = mommy.make('Usuario', user__username='23012616039')

    data = {'cpf_usuario': new_user.user.username,
            'estado': estado.codigo_ibge,
            'municipio': cidade.id}
    form = AlterarCadastradorForm(data=data)
    form.is_valid()
    sistema = form.save()

    assert sistema.cadastrador == new_user