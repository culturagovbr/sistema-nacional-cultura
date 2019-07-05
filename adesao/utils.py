import re

from threading import Thread

from django.forms.models import model_to_dict
from adesao.models import SistemaCultura
from django.core.exceptions import ObjectDoesNotExist
from templated_email import send_templated_mail


def limpar_mascara(mascara):
    return ''.join(re.findall('\d+', mascara))


def enviar_email_conclusao(request):
    recipient_list=[request.user.email, request.user.usuario.email_pessoal]

    if request.session.get('sistema_gestor', False):
        recipient_list.append(request.session['sistema_gestor']['email_institucional'])
        recipient_list.append(request.session['sistema_gestor']['email_pessoal'])

    send_templated_mail(
        template_name='conclusao_cadastro',
        from_email='naoresponda@cultura.gov.br',
        recipient_list=recipient_list,
        context={
            'request':request,
        },
    )


def verificar_anexo(sistema, componente):
    try:
        componente = getattr(sistema, componente)
        if componente:
            situacao = componente.get_situacao_display()
            SITUACAO_CONCLUIDA = "Concluída"
            if situacao == "Arquivo aprovado com ressalvas":
                return SITUACAO_CONCLUIDA
            else:
                return situacao
        else:
            return 'Não Possui'
    except (AttributeError, ObjectDoesNotExist) as exceptions:
        return 'Não Possui'


def preenche_planilha(planilha):
    planilha.write(0, 0, "Ente Federado")
    planilha.write(0, 1, "UF")
    planilha.write(0, 2, "Região")
    planilha.write(0, 3, "Cod.IBGE")
    planilha.write(0, 4, "PIB [2016]")
    planilha.write(0, 5, "IDH [2010]")
    planilha.write(0, 6, "População [2018]")
    planilha.write(0, 7, "Faixa Populacional")
    planilha.write(0, 8, "Situação")
    planilha.write(0, 9, "Situação da Lei do Sistema de Cultura")
    planilha.write(0, 10, "Situação do Órgão Gestor")
    planilha.write(0, 11, "Situação do Conselho de Política Cultural")
    planilha.write(0, 12, "Situação do Fundo de Cultura")
    planilha.write(0, 13, "Situação do Plano de Cultura")
    planilha.write(0, 14, "Participou da Conferência Nacional")
    planilha.write(0, 15, "Endereço")
    planilha.write(0, 16, "Bairro")
    planilha.write(0, 17, "CEP")
    planilha.write(0, 18, "Telefone")
    planilha.write(0, 19, "Email Prefeito")
    planilha.write(0, 20, "Email do Cadastrador")
    planilha.write(0, 21, "Email do Gestor de Cultura")
    planilha.write(0, 22, "Localização do processo")
    planilha.write(0, 23, "Última atualização")

    ultima_linha = 0

    for i, sistema in enumerate(SistemaCultura.objects.distinct('ente_federado__cod_ibge').order_by(
        'ente_federado__cod_ibge', 'ente_federado__nome', '-alterado_em'), start=1):
        if sistema.ente_federado:
            if sistema.ente_federado.cod_ibge > 100 or sistema.ente_federado.cod_ibge == 53:
                nome = sistema.ente_federado.nome
            else:
                nome = "Estado de " + sistema.ente_federado.nome
            cod_ibge = sistema.ente_federado.cod_ibge
            regiao = sistema.ente_federado.get_regiao()
            sigla = sistema.ente_federado.sigla
            idh = sistema.ente_federado.idh
            pib = sistema.ente_federado.pib
            populacao = sistema.ente_federado.populacao
            faixa_populacional = sistema.ente_federado.faixa_populacional()

        else:
            nome = "Não cadastrado"
            cod_ibge = "Não cadastrado"
            regiao = "Não encontrada"
            sigla = "Não encontrada"
            idh = "Não encontrado"
            pib = "Não encontrado"
            populacao = "Não encontrada"
            faixa_populacional = "Não encontrada"

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

        if sistema.gestor_cultura:
            email_gestor_cultura = sistema.gestor_cultura.email_institucional
        else:
            email_gestor_cultura = "Não cadastrado"

        local = sistema.localizacao

        planilha.write(i, 0, nome)
        planilha.write(i, 1, sigla)
        planilha.write(i, 2, regiao)
        planilha.write(i, 3, cod_ibge)
        planilha.write(i, 4, pib)
        planilha.write(i, 5, idh)
        planilha.write(i, 6, populacao)
        planilha.write(i, 7, faixa_populacional)
        planilha.write(i, 8, estado_processo)
        planilha.write(i, 9, verificar_anexo(sistema, "legislacao"))
        planilha.write(i, 10, verificar_anexo(sistema, "orgao_gestor"),)
        planilha.write(i, 11, verificar_anexo(sistema, "conselho"),)
        planilha.write(i, 12, verificar_anexo(sistema, "fundo_cultura"))
        planilha.write(i, 13, verificar_anexo(sistema, "plano"))
        planilha.write(i, 14, "Sim" if sistema.conferencia_nacional else "Não")
        planilha.write(i, 15, endereco)
        planilha.write(i, 16, bairro)
        planilha.write(i, 17, cep)
        planilha.write(i, 18, telefone)
        planilha.write(i, 19, email_gestor)
        planilha.write(i, 20, email_cadastrador)
        planilha.write(i, 21, email_gestor_cultura)
        planilha.write(i, 22, local)
        planilha.write(i, 23, sistema.alterado_em.strftime("%d/%m/%Y às %H:%M:%S"))

        ultima_linha = i

    return ultima_linha


def atualiza_session(sistema_cultura, request):
    request.session['sistema_cultura_selecionado'] = model_to_dict(sistema_cultura, exclude=['data_criacao', 'alterado_em',
        'data_publicacao_acordo'])
    request.session['sistema_cultura_selecionado']['alterado_em'] = sistema_cultura.alterado_em.strftime("%d/%m/%Y às %H:%M:%S")

    if sistema_cultura.alterado_por:
        request.session['sistema_cultura_selecionado']['alterado_por'] = sistema_cultura.alterado_por.user.username
    request.session['sistema_situacao'] = sistema_cultura.get_estado_processo_display()
    request.session['sistema_ente'] = model_to_dict(sistema_cultura.ente_federado, fields=['nome', 'cod_ibge'])

    if sistema_cultura.gestor:
        request.session['sistema_gestor'] = model_to_dict(sistema_cultura.gestor, exclude=['termo_posse', 'rg_copia', 'cpf_copia'])
    else:
        if request.session.get('sistema_gestor', False):
            request.session['sistema_gestor'].clear()

    if sistema_cultura.sede:
        request.session['sistema_sede'] = model_to_dict(sistema_cultura.sede)
    else:
        if request.session.get('sistema_sede', False):
            request.session['sistema_sede'].clear()

    if sistema_cultura.gestor_cultura:
        request.session['sistema_gestor_cultura'] = model_to_dict(sistema_cultura.gestor_cultura)
    else:
        if request.session.get('sistema_gestor_cultura', False):
            request.session['sistema_gestor_cultura'].clear()

    request.session.modified = True
