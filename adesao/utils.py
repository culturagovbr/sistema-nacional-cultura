import re

from threading import Thread

from django.forms.models import model_to_dict
from adesao.models import SistemaCultura
from django.core.exceptions import ObjectDoesNotExist
from templated_email import send_templated_mail

from planotrabalho.models import LISTA_SITUACAO_ARQUIVO


def limpar_mascara(mascara):
    return ''.join(re.findall('\d+', mascara))


def enviar_email_conclusao(request):
    recipient_list = [request.user.email, request.user.usuario.email_pessoal]

    if request.session.get('sistema_gestor', False):
        recipient_list.append(request.session['sistema_gestor']['email_institucional'])
        recipient_list.append(request.session['sistema_gestor']['email_pessoal'])

    send_templated_mail(
        template_name='conclusao_cadastro',
        from_email='naoresponda@turismo.gov.br',
        recipient_list=recipient_list,
        context={
            'request': request,
        },
    )


def verificar_anexo(sistema, componente):
    try:
        componente = getattr(sistema, componente)
        if componente:
            situacao = componente.get_situacao_display()
            if situacao == LISTA_SITUACAO_ARQUIVO[3][1]:
                return LISTA_SITUACAO_ARQUIVO[2][1]

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
    planilha.write(0, 10, "Data Adesão")
    planilha.write(0, 11, "Situação do Órgão Gestor")
    planilha.write(0, 12, "CNPJ do Órgão Gestor de Cultura")
    planilha.write(0, 13, "Situação do Comprovante do CNPJ do Órgão Gestor de Cultura")
    planilha.write(0, 14, "Dados Bancários do Órgão Gestor de Cultura")
    planilha.write(0, 15, "Situação da Ata do Conselho de Política Cultural")
    planilha.write(0, 16, "Situação da Lei do Conselho de Política Cultural")
    planilha.write(0, 17, "CNPJ do Fundo de Cultura")
    planilha.write(0, 18, "Situação do Comprovante do CNPJ do Fundo de Cultura")
    planilha.write(0, 19, "Dados Bancários do Fundo de Cultura")
    planilha.write(0, 20, "Situação da Lei do Fundo de Cultura")
    planilha.write(0, 21, "Situação do Plano de Cultura")
    planilha.write(0, 22, "Participou da Conferência Nacional")
    planilha.write(0, 23, "Endereço")
    planilha.write(0, 24, "Bairro")
    planilha.write(0, 25, "CEP")
    planilha.write(0, 26, "Telefone")
    planilha.write(0, 27, "Email Prefeito")
    planilha.write(0, 28, "Email do Cadastrador")
    planilha.write(0, 29, "Email do Gestor de Cultura")
    planilha.write(0, 30, "Localização do processo")
    planilha.write(0, 31, "Última atualização")

    ultima_linha = 0

    for i, sistema in enumerate(SistemaCultura.sistema.distinct('ente_federado__cod_ibge').order_by(
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

        if sistema.sistema.data_publicacao_acordo:
            data_adesao = sistema.data_publicacao_acordo.strftime("%d/%m/%Y")
        else:
            data_adesao ="Não cadastrado"

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

        if sistema.orgao_gestor:
            #print(str(sistema.orgao_gestor))
            if sistema.orgao_gestor.cnpj:  
                orgao_gestor_cnpj = sistema.orgao_gestor.cnpj
            else:
                orgao_gestor_cnpj = "Não cadastrado"

            if sistema.orgao_gestor.comprovante_cnpj_id:
                situacaor_comprovante_cnpj_orgao_gestor = LISTA_SITUACAO_ARQUIVO[sistema.orgao_gestor.comprovante_cnpj.situacao][1]
            else:
                situacaor_comprovante_cnpj_orgao_gestor = "Não possui"

            if sistema.orgao_gestor.agencia:
                dados_bancarios_orgao_gestor = sistema.orgao_gestor.banco + " - AG:" + sistema.orgao_gestor.agencia + " / CC:" + sistema.orgao_gestor.conta
            else:
                dados_bancarios_orgao_gestor = "Não cadastrado"
        else:
            orgao_gestor_cnpj = "Não cadastrado"
            situacaor_comprovante_cnpj_orgao_gestor = "Não possui"
            dados_bancarios_orgao_gestor = "Não cadastrado"

        if sistema.fundo_cultura:
            if sistema.fundo_cultura.cnpj:
                fundo_cultura_cnpj = sistema.fundo_cultura.cnpj
            else:
                fundo_cultura_cnpj = "Não cadastrado"
            if sistema.fundo_cultura.comprovante_cnpj_id:
                situacao_fundo_cultura_comprovante_cnpj = LISTA_SITUACAO_ARQUIVO[sistema.fundo_cultura.comprovante_cnpj.situacao][1]
            else:
                situacao_fundo_cultura_comprovante_cnpj = "Não possui"
            if sistema.fundo_cultura.agencia:
                dados_bancarios_fundo_cultura = sistema.fundo_cultura.banco + " - AG:" + sistema.fundo_cultura.agencia + " / CC:" + sistema.fundo_cultura.conta
            else:
                dados_bancarios_fundo_cultura = "Não cadastrado"
        else:
            fundo_cultura_cnpj = "Não cadastrado"
            situacao_fundo_cultura_comprovante_cnpj = "Não possui"
            dados_bancarios_fundo_cultura = "Não cadastrado"

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
        planilha.write(i, 10, data_adesao)
        planilha.write(i, 11, verificar_anexo(sistema, "orgao_gestor"),)
        planilha.write(i, 12, orgao_gestor_cnpj)
        planilha.write(i, 13, situacaor_comprovante_cnpj_orgao_gestor)
        planilha.write(i, 14, dados_bancarios_orgao_gestor)
        planilha.write(i, 15, verificar_anexo(sistema, "conselho"),)
        planilha.write(i, 16, verificar_anexo(sistema.conselho, "lei"))
        planilha.write(i, 17, fundo_cultura_cnpj)
        planilha.write(i, 18, situacao_fundo_cultura_comprovante_cnpj)
        planilha.write(i, 19, dados_bancarios_fundo_cultura)
        planilha.write(i, 20, verificar_anexo(sistema, "fundo_cultura"))
        planilha.write(i, 21, verificar_anexo(sistema, "plano"))
        planilha.write(i, 22, "Sim" if sistema.conferencia_nacional else "Não")
        planilha.write(i, 23, endereco)
        planilha.write(i, 24, bairro)
        planilha.write(i, 25, cep)
        planilha.write(i, 26, telefone)
        planilha.write(i, 27, email_gestor)
        planilha.write(i, 28, email_cadastrador)
        planilha.write(i, 29, email_gestor_cultura)
        planilha.write(i, 30, local)
        planilha.write(i, 31, sistema.alterado_em.strftime("%d/%m/%Y às %H:%M:%S"))

        ultima_linha = i

    return ultima_linha


def atualiza_session(sistema_cultura, request):
    request.session['sistema_cultura_selecionado'] = model_to_dict(sistema_cultura, exclude=['data_criacao', 'alterado_em',
                                                                                             'data_publicacao_acordo', 'data_publicacao_retificacao', 'oficio_prorrogacao_prazo', 'oficio_cadastrador'])
    request.session['sistema_cultura_selecionado']['alterado_em'] = sistema_cultura.alterado_em.strftime(
        "%d/%m/%Y às %H:%M:%S")

    if sistema_cultura.alterado_por:
        request.session['sistema_cultura_selecionado']['alterado_por'] = sistema_cultura.alterado_por.user.username
    request.session['sistema_situacao'] = sistema_cultura.get_estado_processo_display()
    request.session['sistema_ente'] = model_to_dict(
        sistema_cultura.ente_federado, fields=['nome', 'cod_ibge',])

    for item in request.session['sistemas']:
        for item2 in request.session['sistema_ente']:
            if str(request.session['sistema_ente'][item2]) in str(item['ente_federado__nome']):
                request.session['sistema_ente'][item2] = str(item['ente_federado__nome'])


    if sistema_cultura.gestor:
        request.session['sistema_gestor'] = model_to_dict(
            sistema_cultura.gestor, exclude=['termo_posse', 'rg_copia', 'cpf_copia'])
    else:
        if request.session.get('sistema_gestor', False):
            request.session['sistema_gestor'].clear()

    if sistema_cultura.sede:
        request.session['sistema_sede'] = model_to_dict(sistema_cultura.sede)
    else:
        if request.session.get('sistema_sede', False):
            request.session['sistema_sede'].clear()

    if sistema_cultura.gestor_cultura:
        request.session['sistema_gestor_cultura'] = model_to_dict(
            sistema_cultura.gestor_cultura)
        request.session['sistema_gestor_cultura']['estado_expeditor_sigla'] = sistema_cultura.gestor_cultura.estado_expeditor.sigla

    else:
        if request.session.get('sistema_gestor_cultura', False):
            request.session['sistema_gestor_cultura'].clear()

    request.session.modified = True


def ir_para_estado_envio_documentacao(request):
    ente_federado = request.session.get('sistema_ente', False)
    gestor_cultura = request.session.get('sistema_gestor_cultura', False)
    sistema = request.session.get('sistema_cultura_selecionado', False)

    if ente_federado and \
            gestor_cultura and \
            sistema and int(sistema['estado_processo']) < 1:
        sistema = SistemaCultura.sistema.get(id=sistema['id'])
        sistema.estado_processo = "1"
        sistema.save()

        sistema_atualizado = SistemaCultura.sistema.get(
            ente_federado__cod_ibge=ente_federado['cod_ibge'])
        atualiza_session(sistema_atualizado, request)

        enviar_email_conclusao(request)

def concatenacao_municipi_uf(sistemas_cultura):
    sistema_ente_federados = list(sistemas_cultura.values('id', 'ente_federado__nome'))

    for item in sistemas_cultura:
        for item2 in sistema_ente_federados:
            if item2['ente_federado__nome'] in str(item.ente_federado):
                item2['ente_federado__nome'] = str(item.ente_federado)

    return sistema_ente_federados
