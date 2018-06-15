import pytest

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core import mail
from django.conf import settings

from model_mommy import mommy

from .models import Municipio

pytestmark = pytest.mark.django_db

def testa_envio_email_em_nova_adesao(client):
    user = User.objects.create(username='teste')
    user.set_password('123456')
    user.save()
    usuario = mommy.make('Usuario',user=user)

    estado = mommy.make('Uf')
    cidade = mommy.make('Cidade')

    login = client.login(username=user.username,password='123456')

    response = client.post('/adesao/municipio/cadastrar/0/', {'estado':estado.codigo_ibge,'cidade':cidade.id,
        'cnpj_prefeitura':'95.876.554/0001-63', 'cpf_prefeito':'381.390.630-29','uf': estado,
        'rg_prefeito':'48.464.068-9','orgao_expeditor_rg':'SSP','estado_expeditor':estado.codigo_ibge,
        'nome_prefeito':'Joao silva','email_institucional_prefeito':'joao@email.com',
        'endereco_eletronico':'teste.com.br','cep':'60751-110','complemento': 'casa 22',
        'bairro':'rua teste','telefone_um':'6299999999','endereco':'rua do pao',
        'termo_posse_prefeito': SimpleUploadedFile('test_file.pdf', bytes('test text','utf-8')),
        'cpf_copia_prefeito': SimpleUploadedFile('test_file2.pdf', bytes('test text','utf-8')),
        'rg_copia_prefeito': SimpleUploadedFile('test_file2.pdf', bytes('test text','utf-8')),
        })

    # Acessa a url de sucesso após o cadastro para fazer o envio do email
    success_url = client.get(response.url)

    municipio = Municipio.objects.last()

    assert len(mail.outbox) == 1
    assert mail.outbox[0].subject == 'MINISTÉRIO DA CULTURA - SNC - SOLICITAÇÃO NOVA ADESÃO'
    assert mail.outbox[0].from_email == 'naoresponda@cultura.gov.br'
    assert mail.outbox[0].to == [settings.RECEIVER_EMAIL]
    assert mail.outbox[0].body == ('Prezado Gestor,\n' +
            'Um novo ente federado acabou de se cadastrar e fazer a solicitação de nova adesão.\n' +
            'Segue abaixo os dados de contato do ente federado:\n\n' +
            'Dados do Ente Federado:\n' +
            'Cadastrador: ' + usuario.nome_usuario + '\n' +
            'Nome do Prefeito: ' + municipio.nome_prefeito + '\n' +
            'Cidade: ' + cidade.nome_municipio + '\n' +
            'Estado: ' + estado.sigla + '\n' +
            'Email Institucional: ' + municipio.email_institucional_prefeito + '\n' +
            'Telefone de Contato: ' + municipio.telefone_um + '\n' +
            'Link da Adesão: ' + 'http://snc.cultura.gov.br/gestao/detalhar/municipio/{}'.format(usuario.id) + '\n\n' +
            'Equipe SNC\nMinistério da Cultura')


def testa_envio_email_em_esqueceu_senha(client):
    site = mommy.make('Site', name="SNC", domain="snc.cultura.gov.br")

    user = User.objects.create(username='teste',email='test@email.com')
    user.set_password('123456')
    user.save()
    usuario = mommy.make('Usuario',user=user)

    response = client.post('/password_reset/',{'email': usuario.user.email})

    assert len(mail.outbox) == 1


def testa_template_em_esqueceu_senha(client):
    '''
    Testa qual template é utilizado na tela de redefinição de senha.
    '''

    response = client.get('/password_reset/')

    assert response.template_name == 'registration/password_reset_form.html' 

    assert "Sistema Nacional de Cultura"  in response.rendered_content
