import pytest

from planotrabalho.forms import CriarFundoForm

from django.core.files.uploadedfile import SimpleUploadedFile

def test_criar_fundo_form_cnpj_igual_sede(client, login, sistema_cultura, cnpj):
    """Testa se dá erro ao cadastrar fundo de cultura com 
    o mesmo CNPJ cadastrado no ente"""

    data = {
            "data_publicacao": "28/06/2018",
            "cnpj": "28.134.084/0001-75", 
            "mesma_lei": "False", 
            "possui_cnpj": "True"
    }

    form = CriarFundoForm(logged_user=login.user, sistema=sistema_cultura,
        tipo="fundo_cultura", data=data, files={"arquivo": SimpleUploadedFile(
                "componente.txt", b"file_content", content_type="text/plain"
            ),
            "comprovante": SimpleUploadedFile(
                "comprovante.txt", b"file_content", content_type="text/plain"
            )
        })

    assert not form.is_valid()
    assert form.errors == {'cnpj': ['CNPJ já cadastrado no ente, insira um CNPJ exclusivo do fundo de cultura']}
