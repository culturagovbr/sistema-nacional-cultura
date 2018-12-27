import re

from threading import Thread

from django.core.mail import send_mail
from django.forms.models import model_to_dict
from adesao.models import SistemaCultura
from django.core.exceptions import ObjectDoesNotExist


def validar_cpf(cpf):
    digitos = [int(c) for c in cpf if c.isdigit()]
    if len(digitos) == 11:
        a, b, c, d, e, f, g, h, i, j, k = digitos
        numeros = [a, b, c, d, e, f, g, h, i]
        r = range(10, 1, -1)
        soma = sum([x * y for x, y in zip(numeros, r)])
        resto = soma % 11
        dv1 = (11 - resto if 11 - resto < 10 else 0)
        numeros = [a, b, c, d, e, f, g, h, i, dv1]
        r = range(11, 1, -1)
        soma = sum([x*y for x, y in zip(numeros, r)])
        resto = soma % 11
        dv2 = (11 - resto if 11 - resto < 10 else 0)
        return dv1 == j and dv2 == k
    return False


def validar_cnpj(cnpj):
    """
    Valida CNPJs, retornando apenas a string de números válida.

    # CNPJs errados
    >>> validar_cnpj('abcdefghijklmn')
    False
    >>> validar_cnpj('123')
    False
    >>> validar_cnpj('')
    False
    >>> validar_cnpj(None)
    False
    >>> validar_cnpj('12345678901234')
    False
    >>> validar_cnpj('11222333000100')
    False

    # CNPJs corretos
    >>> validar_cnpj('11222333000181')
    '11222333000181'
    >>> validar_cnpj('11.222.333/0001-81')
    '11222333000181'
    >>> validar_cnpj('  11 222 333 0001 81  ')
    '11222333000181'
    """

    cnpj = ''.join(re.findall('\d', str(cnpj)))

    if (not cnpj) or (len(cnpj) < 14):
        return False

    inteiros = list(map(int, cnpj))
    novo = inteiros[:12]

    prod = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    while len(novo) < 14:
        r = sum([x * y for (x, y) in zip(novo, prod)]) % 11
        if r > 1:
            f = 11 - r
        else:
            f = 0
        novo.append(f)
        prod.insert(0, 6)

    if novo == inteiros:
        return cnpj
    return False


def limpar_mascara(mascara):
    return ''.join(re.findall('\d+', mascara))


def enviar_email_conclusao(user, message_txt, message_html):
    Thread(target=send_mail, args=(
        'Sistema Nacional de Cultura - Solicitação de Adesão ao SNC',
        message_txt,
        'naoresponda@cultura.gov.br',
        [user.email],),
        kwargs = {'fail_silently': 'False', 'html_message': message_html}
        ).start()


def verificar_anexo(sistema, componente):
    try:
        componente = getattr(sistema, componente)
        if componente:
            return componente.get_situacao_display()
        else:
            return 'Não Possui'
    except (AttributeError, ObjectDoesNotExist) as exceptions:
        return 'Não Possui'


def preenche_planilha(planilha):
    planilha.write(0, 0, "Ente Federado")
    planilha.write(0, 1, "Cod.IBGE")
    planilha.write(0, 2, "Situação")
    planilha.write(0, 3, "Situação da Lei do Sistema de Cultura")
    planilha.write(0, 4, "Situação do Órgão Gestor")
    planilha.write(0, 5, "Situação do Conselho de Política Cultural")
    planilha.write(0, 6, "Situação do Fundo de Cultura")
    planilha.write(0, 7, "Situação do Plano de Cultura")
    planilha.write(0, 8, "Endereço")
    planilha.write(0, 9, "Bairro")
    planilha.write(0, 10, "CEP")
    planilha.write(0, 11, "Telefone")
    planilha.write(0, 12, "Email Prefeito")
    planilha.write(0, 13, "Email do Cadastrador")
    planilha.write(0, 14, "Email do Responsável")
    planilha.write(0, 15, "Localização do processo")
    ultima_linha = 0

    for i, sistema in enumerate(SistemaCultura.sistema.all(), start=1):
        if sistema.ente_federado:
            if sistema.ente_federado.is_municipio:
                nome = sistema.ente_federado.__str__()
            else:
                nome = "Estado de " + sistema.ente_federado.nome
            cod_ibge = sistema.ente_federado.cod_ibge
        else:
            nome = "Nome não cadastrado"
            cod_ibge = "Código não cadastrado"

        estado_processo = sistema.get_estado_processo_display()

        if sistema.sede:
            endereco = sistema.sede.endereco
            bairro = sistema.sede.bairro
            cep = sistema.sede.cep
            telefone = sistema.sede.telefone_um
        else:
            endereco = "Não cadastrado"
            bairro = "Não cadastrado"
            cep = "Não cadastrado"
            telefone = "Não cadastrado"

        if sistema.gestor:
            email_gestor = sistema.gestor.email_institucional
        else:
            email_gestor = "Não cadastrado"

        if sistema.cadastrador:
            email_cadastrador = sistema.cadastrador.user.email
        else:
            email_cadastrador = "Não cadastrado"

        if sistema.responsavel:
            email_responsavel = sistema.responsavel.email_institucional
        else:
            email_responsavel = "Não cadastrado"

        local = sistema.localizacao

        planilha.write(i, 0, nome)
        planilha.write(i, 1, cod_ibge)
        planilha.write(i, 2, estado_processo)
        planilha.write(i, 3, verificar_anexo(sistema, "legislacao"))
        planilha.write(i, 4, verificar_anexo(sistema, "orgao_gestor"),)
        planilha.write(i, 5, verificar_anexo(sistema, "conselho"),)
        planilha.write(i, 6, verificar_anexo(sistema, "fundo_cultura"))
        planilha.write(i, 7, verificar_anexo(sistema, "plano"))
        planilha.write(i, 8, endereco)
        planilha.write(i, 9, bairro)
        planilha.write(i, 10, cep)
        planilha.write(i, 11, telefone)
        planilha.write(i, 12, email_gestor)
        planilha.write(i, 13, email_cadastrador)
        planilha.write(i, 14, email_responsavel)
        planilha.write(i, 15, local)

        ultima_linha = i

    return ultima_linha


def atualiza_session(sistema_cultura, request):
    request.session['sistema_cultura_selecionado'] = model_to_dict(sistema_cultura, exclude=['data_criacao', 'alterado_em'])
    request.session['sistema_situacao'] = sistema_cultura.get_estado_processo_display()
    request.session['sistema_sede'] = model_to_dict(sistema_cultura.sede)
    request.session['sistema_gestor'] = model_to_dict(sistema_cultura.gestor, exclude=['termo_posse', 'rg_copia', 'cpf_copia'])
    request.session['sistema_ente'] = model_to_dict(sistema_cultura.ente_federado, fields=['nome'])

    if sistema_cultura.responsavel:
        request.session['sistema_responsavel'] = model_to_dict(sistema_cultura.responsavel)

    if sistema_cultura.secretario:
        request.session['sistema_secretario'] = model_to_dict(sistema_cultura.secretario)
   
    request.session.modified = True