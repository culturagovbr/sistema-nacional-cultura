from adesao.models import SistemaCultura

from planotrabalho.models import LISTA_PERIODICIDADE, LISTA_ESFERAS_FEDERACAO, LISTA_PERFIL_PARTICIPANTE_CURSOS
from django.db.models import Q
from django.db import connection


def preenche_planilha(planilha, codigos):
    planilha.write(0, 0, "Ente federado")
    planilha.write(0, 1, "UF")
    planilha.write(0, 2, "Data da adesão")
    planilha.write(0, 3, "Lei Sistema")
    planilha.write(0, 4, "Data Publicação Lei")
    planilha.write(0, 5, "Órgão Gestor de Cultura")
    planilha.write(0, 6, "Data da Publicação Lei (Normativo)")
    planilha.write(0, 7, "Perfil órgão gestor de cultura")
    planilha.write(0, 8, "Lei Fundo Cultural")
    planilha.write(0, 9, "Mesma lei do sistema de cultura")
    planilha.write(0, 10, "Possui CNPJ?")
    planilha.write(0, 11, "CNPJ")
    planilha.write(0, 12, "Lei Plano de Cultura")
    planilha.write(0, 13, "Plano é Exclusivo de Cultura?")
    planilha.write(0, 14, "Data Publicação da Lei (Plano)")
    planilha.write(0, 15, "Lei possuí anexo?")
    planilha.write(0, 16, "Último ano vingência do Plano de Cultura?")
    planilha.write(0, 17, "Qual a periodicidade do plano?")
    planilha.write(0, 18, "Possui metas?")
    planilha.write(0, 19, "O plano é monitorado?")
    planilha.write(0, 20,
                   "Para a construção do Plano de Cultura, o ente federado participou de algum Programa de Formação de Gestores e Conselheiros Culturais?")
    planilha.write(0, 21, "Indique o ano de início do curso")
    planilha.write(0, 22, "Indique o ano de término do curso")
    planilha.write(0, 23, "Indique por qual esfera da federação foi ofertado o curso")
    planilha.write(0, 24, "Indique o tipo de curso")
    planilha.write(0, 25, "Qual o perfil do participante?")
    planilha.write(0, 26, "Lei do Conselho de Cultura")
    planilha.write(0, 27, "Data de publicação da lei")
    planilha.write(0, 28, "Possui alguma ata de última reunião do conselho?")
    planilha.write(0, 29, "O conselho é exclusivo de cultura?")
    planilha.write(0, 30, "O conselho é paritário?")

    ultima_linha = 0
    codigosWhere = []
    for codigo in codigos:
        codigosWhere.append(codigo)

    sistemaCultura = SistemaCultura.sistema.filter(
        ente_federado__isnull=False).filter(pk__in=codigosWhere)

    for i, sistema in enumerate(sistemaCultura, start=1):
        if sistema.ente_federado:
            nome = "Estado de " + sistema.ente_federado.nome
            if sistema.ente_federado.cod_ibge > 100 or \
                sistema.ente_federado.cod_ibge == 53:
                nome = sistema.ente_federado.nome
            else:
                nome = "Não cadastrado"

        if sistema.data_publicacao_acordo:
            data_publicacao_acordo = sistema.data_publicacao_acordo.strftime("%d/%m/%Y")
        else:
            data_publicacao_acordo = "Não cadastrado"
        situacoes = sistema.get_situacao_componentes()

        planilha.write(i, 0, nome)
        planilha.write(i, 1, sistema.ente_federado.sigla)
        planilha.write(i, 2, data_publicacao_acordo)
        planilha.write(i, 3, situacoes.get('legislacao'))
        if sistema.legislacao:
            if sistema.legislacao.data_publicacao:
                planilha.write(i, 4, sistema.legislacao.data_publicacao.strftime("%d/%m/%Y"))
        planilha.write(i, 5, situacoes.get('orgao_gestor'))
        if sistema.orgao_gestor:
            if sistema.orgao_gestor.data_publicacao:
                planilha.write(i, 6, sistema.orgao_gestor.data_publicacao.strftime("%d/%m/%Y"))
            perfil_gestor = sistema.orgao_gestor.get_perfil_display()
            planilha.write(i, 7, perfil_gestor)
        planilha.write(i, 8, situacoes.get('fundo_cultura'))
        if sistema.legislacao and sistema.fundo_cultura:
            mesma_lei = (sistema.legislacao.arquivo == sistema.fundo_cultura.arquivo and 'Sim' or 'Não')
            planilha.write(i, 9, mesma_lei)
        if sistema.fundo_cultura:
            if sistema.fundo_cultura.cnpj:
                planilha.write(i, 10, 'Sim')
                if len(sistema.fundo_cultura.cnpj) == 14:
                    cnpj = '{}.{}.{}/{}-{}'.format(sistema.fundo_cultura.cnpj[:2], sistema.fundo_cultura.cnpj[2:5],
                                                   sistema.fundo_cultura.cnpj[5:7], sistema.fundo_cultura.cnpj[7:11],
                                                   sistema.fundo_cultura.cnpj[11:])

                    planilha.write(i, 11, cnpj)
                else:
                    planilha.write(i, 11, sistema.fundo_cultura.cnpj)
            else:
                planilha.write(i, 10, 'Não')
        planilha.write(i, 12, situacoes.get('plano'))
        if sistema.plano:
            planilha.write(i, 13, (sistema.plano.exclusivo_cultura and 'Sim' or 'Não'))
            if sistema.plano.data_publicacao:
                planilha.write(i, 14, sistema.plano.data_publicacao.strftime("%d/%m/%Y"))
            planilha.write(i, 15, (sistema.plano.anexo_na_lei and 'Sim' or 'Não'))
            planilha.write(i, 16, sistema.plano.ultimo_ano_vigencia)

            if sistema.plano.periodicidade:
                planilha.write(i, 17, dict(LISTA_PERIODICIDADE).get(int(sistema.plano.periodicidade)))

            possui_metas = (sistema.plano.metas and 'Sim' or 'Não')
            planilha.write(i, 18, possui_metas)
            planilha.write(i, 19, (sistema.plano.local_monitoramento and 'Sim' or 'Não'))
            participou_cursos = (sistema.plano.tipo_curso and 'Sim' or 'Não')
            planilha.write(i, 20, participou_cursos)
            if sistema.plano.ano_inicio_curso:
                planilha.write(i, 21, sistema.plano.ano_inicio_curso)
            if sistema.plano.ano_termino_curso:
                planilha.write(i, 22, sistema.plano.ano_termino_curso)
            if sistema.plano.esfera_federacao_curso:
                esferas = map(lambda esfera: dict(LISTA_ESFERAS_FEDERACAO).get(int(esfera)),
                              sistema.plano.esfera_federacao_curso)
                planilha.write(i, 23, ', '.join(esferas))
            if sistema.plano.tipo_curso:
                planilha.write(i, 24, sistema.plano.tipo_curso)
            if sistema.plano.perfil_participante:
                perfils = map(lambda perfil: dict(LISTA_PERFIL_PARTICIPANTE_CURSOS).get(int(perfil)),
                              sistema.plano.perfil_participante)
                planilha.write(i, 25, ', '.join(perfils))

        planilha.write(i, 26, situacoes.get('conselho'))
        if sistema.conselho:
            if sistema.conselho.data_publicacao:
                planilha.write(i, 27, sistema.conselho.data_publicacao.strftime("%d/%m/%Y"))
            possui_arquivo_ata = (sistema.conselho.arquivo and 'Sim' or 'Não')
            planilha.write(i, 28, possui_arquivo_ata)
            conselho_exclusivo = (sistema.conselho.exclusivo_cultura and 'Sim' or 'Não')
            planilha.write(i, 29, conselho_exclusivo)
            planilha.write(i, 30, (sistema.conselho.paritario and 'Sim' or 'Não'))

        ultima_linha = i

    return ultima_linha
