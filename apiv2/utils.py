from adesao.models import (Cidade, Municipio, SistemaCultura)

from planotrabalho.models import LISTA_PERIODICIDADE, LISTA_ESFERAS_FEDERACAO, LISTA_PERFIL_PARTICIPANTE_CURSOS, LISTA_SITUACAO_ARQUIVO
from django.db.models import Q
from django.db import connection


def preenche_planilha(planilha, codigos):

    planilha.write(0, 0, "Ente federado")
    planilha.write(0, 1, "UF")
    planilha.write(0, 2, "Data da adesão")
    planilha.write(0, 3, "Situação da lei do Sistema de Cultura")
    planilha.write(0, 4, "Data Publicação da Lei do Sistema de Culura")
    planilha.write(0, 5, "Lei do Órgão Gestor de Cultura")
    planilha.write(0, 6, "Data de publicação da Lei do Órgão Gestor de Cultura")
    planilha.write(0, 7, "Perfil órgão gestor de cultura")
    planilha.write(0, 8, "Situação da Lei do Fundo de Cultura")
    planilha.write(0, 9, "Data da Publicação da Lei do Fundo de Cultura (Normativo)")
    planilha.write(0, 10, "Mesma lei do sistema de cultura?")
    planilha.write(0, 11, "Possui CNPJ do Fundo de Cultura?")
    planilha.write(0, 12, "Situação da Lei do Plano de Cultura")
    planilha.write(0, 13, "Plano é Exclusivo de Cultura?")
    planilha.write(0, 14, "Data da Publicação da Lei do Plano de Cultura (Normativo)")
    planilha.write(0, 15, "Lei do Plano possui anexo?")
    planilha.write(0, 16, "Último ano de vingência do Plano de Cultura?")
    planilha.write(0, 17, "Qual a periodicidade do Plano de Cultura?")
    planilha.write(0, 18, "Situação Metas do Plano")
    planilha.write(0, 19, "O Plano de Cultura possui metas?")
    planilha.write(0, 20, "O Plano de Cultura é monitorado?")
    planilha.write(0, 21, "Para a construção do Plano de Cultura, o ente federado participou de algum Programa de Formação de Gestores e Conselheiros Culturais?")
    planilha.write(0, 22, "Indique o ano de início do curso")
    planilha.write(0, 23, "Indique o ano de término do curso")
    planilha.write(0, 24, "Indique por qual esfera da federação foi ofertado o curso")
    planilha.write(0, 25, "Indique o tipo de curso")
    planilha.write(0, 26, "Qual o perfil do participante?")
    planilha.write(0, 27, "Situação da Lei do Conselho de Cultura")
    planilha.write(0, 28, "Data de publicação da Lei do Conselho de Cultura (Normativo)")
    planilha.write(0, 29, "Situação Ata do Conselho")
    planilha.write(0, 30, "Possui alguma ata da última reunião do Conselho de Cultura?")
    planilha.write(0, 31, "O Conselho é exclusivo de cultura?")
    planilha.write(0, 32, "O Conselho é paritário?")
    planilha.write(0, 33, "Órgão Gestor CNPJ Situação")
    planilha.write(0, 34, "Órgão Gestor CNPJ")
    planilha.write(0, 35, "Órgão Gestor - dados bancários")
    planilha.write(0, 36, "Fundo de Cultura CNPJ Situação")
    planilha.write(0, 37, "Fundo de Cultura CNPJ")
    planilha.write(0, 38, "Fundo de Cultura - dados bancários")
    planilha.write(0, 39, "População")
    planilha.write(0, 40, "IDH")
    planilha.write(0, 41, "PIB")
    planilha.write(0, 42, "Prefeito")
    planilha.write(0, 43, "Gestor de Cultura")
    planilha.write(0, 44, "E-mail")
    planilha.write(0, 45, "Telefone")
    planilha.write(0, 46, "Endereço")
    planilha.write(0, 47, "CEP")

    ultima_linha = 0
    codigosWhere = []
    for codigo in codigos:
        codigosWhere.append(codigo)

    sistemaCultura = SistemaCultura.sistema.filter(
        ente_federado__isnull=False).filter(pk__in=codigosWhere)

    for i, sistema in enumerate(sistemaCultura, start=1):

        valores_colunas = []

        # Coluna 0
        if sistema.ente_federado:
            if sistema.ente_federado.cod_ibge > 100 or sistema.ente_federado.cod_ibge == 53:
                valores_colunas.append(sistema.ente_federado.nome)
            elif sistema.ente_federado.cod_ibge < 100 and sistema.ente_federado.cod_ibge != 53:
                valores_colunas.append("Estado de " + sistema.ente_federado.nome)
            else:
                valores_colunas.append("Não cadastrado")
        else:
            valores_colunas.append("Não cadastrado")

        # Coluna 1
        valores_colunas.append(sistema.ente_federado.sigla)

        # Coluna 2
        if sistema.data_publicacao_acordo:
            valores_colunas.append(sistema.data_publicacao_acordo.strftime("%d/%m/%Y"))
        else:
            valores_colunas.append("Não cadastrado")

        # Coluna 3
        situacoes = sistema.get_situacao_componentes()

        # Coluna 4
        valores_colunas.append(situacoes.get('legislacao'))

        if sistema.legislacao:
            if sistema.legislacao.data_publicacao:
                valores_colunas.append(sistema.legislacao.data_publicacao.strftime("%d/%m/%Y"))
            else:
                valores_colunas.append('')
        else:
            valores_colunas.append('')

        # Coluna 5
        valores_colunas.append(situacoes.get('orgao_gestor'))

        # Coluna 6 e 7
        if sistema.orgao_gestor:
            if sistema.orgao_gestor.data_publicacao:
                valores_colunas.append(sistema.orgao_gestor.data_publicacao.strftime("%d/%m/%Y"))
            else:
                valores_colunas.append('')
            perfil_gestor = sistema.orgao_gestor.get_perfil_display()
            valores_colunas.append(perfil_gestor)
        else:
            valores_colunas.append('')
            valores_colunas.append('')
            
        # Coluna 8 e 9
        valores_colunas.append(situacoes.get('fundo_cultura'))

        if sistema.fundo_cultura:
            if sistema.fundo_cultura.data_publicacao:
                valores_colunas.append(sistema.fundo_cultura.data_publicacao.strftime("%d/%m/%Y"))
            else:
                valores_colunas.append('')
        else:
            valores_colunas.append('')

        # Coluna 10
        if sistema.legislacao and sistema.fundo_cultura:
            mesma_lei = (sistema.legislacao.arquivo == sistema.fundo_cultura.arquivo and 'Sim' or 'Não')
            valores_colunas.append(mesma_lei)
        else:
            valores_colunas.append('')

        # Coluna 11
        if sistema.fundo_cultura:
            if sistema.fundo_cultura.cnpj:
                valores_colunas.append((sistema.fundo_cultura.cnpj and 'Sim' or 'Não'))
            else:
                valores_colunas.append('Não')
        else:
            valores_colunas.append('Não')

        # Coluna 12 a 26
        valores_colunas.append(situacoes.get('plano'))

        if sistema.plano:
            # Coluna 13
            valores_colunas.append((sistema.plano.exclusivo_cultura and 'Sim' or 'Não'))

            # Coluna 14
            if sistema.plano.data_publicacao:
                valores_colunas.append(sistema.plano.data_publicacao.strftime("%d/%m/%Y"))
            else:   
                valores_colunas.append("Não informada")

            # Coluna 15
            valores_colunas.append((sistema.plano.anexo_na_lei and 'Sim' or 'Não'))

            # Coluna 16
            if sistema.plano.ultimo_ano_vigencia:
                valores_colunas.append(sistema.plano.ultimo_ano_vigencia)
            else:
                valores_colunas.append('')

            # Coluna 17
            if sistema.plano.periodicidade:
                valores_colunas.append(dict(LISTA_PERIODICIDADE).get(
                    int(sistema.plano.periodicidade)))
            else:
                valores_colunas.append('')

            # Coluna 18
            if sistema.plano.metas: 
                valores_colunas.append(LISTA_SITUACAO_ARQUIVO[sistema.plano.metas.situacao][1]) 
                valores_colunas.append((sistema.plano.metas and 'Sim' or 'Não'))
            else:
                valores_colunas.append('')
                valores_colunas.append('Não')
            
            # Coluna 19 e 20
            valores_colunas.append((sistema.plano.local_monitoramento and 'Sim' or 'Não'))

            # Coluna 21
            valores_colunas.append((sistema.plano.tipo_curso and 'Sim' or 'Não'))
            
            # Coluna 22
            if sistema.plano.ano_inicio_curso:
                valores_colunas.append(sistema.plano.ano_inicio_curso)
            else:
                valores_colunas.append('')

            # Coluna 23
            if sistema.plano.ano_termino_curso:
                valores_colunas.append(sistema.plano.ano_termino_curso)
            else:
                valores_colunas.append('')
                
            # Coluna 24
            if sistema.plano.esfera_federacao_curso:
                esferas = map(lambda esfera: dict(LISTA_ESFERAS_FEDERACAO).get(int(esfera)),
                            sistema.plano.esfera_federacao_curso)
                valores_colunas.append(', '.join(esferas))
            else:
                valores_colunas.append('')
                
            # Coluna 25
            if sistema.plano.tipo_curso:
                valores_colunas.append(sistema.plano.tipo_curso)
            else:
                valores_colunas.append('')
                
            # Coluna 26
            if sistema.plano.perfil_participante:
                if len(sistema.plano.perfil_participante) > 0:
                    perfils = map(lambda perfil: dict(LISTA_PERFIL_PARTICIPANTE_CURSOS).get(int(perfil)),
                                sistema.plano.perfil_participante)
                    valores_colunas.append(', '.join(perfils))
                else:
                    valores_colunas.append('')
            else:
                valores_colunas.append('')
        else:
            # Se não dados das colunas 13 a 26
            valores_colunas.append('') 
            valores_colunas.append('')
            valores_colunas.append('')
            valores_colunas.append('')
            valores_colunas.append('')
            valores_colunas.append('')
            valores_colunas.append('') 
            valores_colunas.append('')
            valores_colunas.append('')
            valores_colunas.append('')
            valores_colunas.append('')
            valores_colunas.append('')
            valores_colunas.append('')
            valores_colunas.append('')

        # Coluna 27
        valores_colunas.append(situacoes.get('conselho'))

        if sistema.conselho:
            # Coluna 28
            if sistema.conselho.data_publicacao:
                valores_colunas.append(sistema.conselho.data_publicacao.strftime("%d/%m/%Y"))
            else:
                valores_colunas.append('')
            
            # Coluna 29
            if sistema.conselho.lei:
                valores_colunas.append(LISTA_SITUACAO_ARQUIVO[sistema.conselho.lei.situacao][1])
            else:
                valores_colunas.append('')

            # Coluna 30
            valores_colunas.append((sistema.conselho.arquivo and 'Sim' or 'Não'))
            
            # Coluna 31
            valores_colunas.append((sistema.conselho.exclusivo_cultura and 'Sim' or 'Não'))
            
            # Coluna 32
            valores_colunas.append((sistema.conselho.paritario and 'Sim' or 'Não'))
                

        if sistema.orgao_gestor:
            # Coluna 33
            if sistema.orgao_gestor.comprovante_cnpj:
                valores_colunas.append(sistema.orgao_gestor.comprovante_cnpj.situacao)
            else:
                valores_colunas.append('')

            # Coluna 34
            if sistema.orgao_gestor.cnpj:
                if len(sistema.orgao_gestor.cnpj) == 14:
                    cnpj = '{}.{}.{}/{}-{}'.format(sistema.orgao_gestor.cnpj[:2], sistema.orgao_gestor.cnpj[2:5],
                                                sistema.orgao_gestor.cnpj[5:7], sistema.orgao_gestor.cnpj[7:11],
                                                sistema.orgao_gestor.cnpj[11:])
                    valores_colunas.append(cnpj)
                else:
                    valores_colunas.append(sistema.orgao_gestor.cnpj)
            else:
                valores_colunas.append('')

            # Coluna 35
            if sistema.orgao_gestor.banco != '0' and sistema.orgao_gestor.banco != None :
                valores_colunas.append('Sim')
            else:
                valores_colunas.append('Não')
        else:
            # Se não valores Coluna 33 a 35
            valores_colunas.append('')
            valores_colunas.append('')
            valores_colunas.append('Não')

        if sistema.fundo_cultura:
            # Coluna 36
            if sistema.fundo_cultura.comprovante_cnpj:
                valores_colunas.append(sistema.fundo_cultura.comprovante_cnpj.situacao)
            else:
                valores_colunas.append('')

            if sistema.fundo_cultura.cnpj:
                # Coluna 37
                if len(sistema.fundo_cultura.cnpj) == 14:
                    cnpj = '{}.{}.{}/{}-{}'.format(sistema.fundo_cultura.cnpj[:2], sistema.fundo_cultura.cnpj[2:5],
                                                sistema.fundo_cultura.cnpj[5:7], sistema.fundo_cultura.cnpj[7:11],
                                                sistema.fundo_cultura.cnpj[11:])
                    valores_colunas.append(cnpj)
                else:
                    valores_colunas.append(sistema.fundo_cultura.cnpj)
            else:
                valores_colunas.append('')

            # Coluna 38
            if sistema.fundo_cultura.banco != '0' and sistema.fundo_cultura.banco != None:
                valores_colunas.append('Sim')
            else:
                valores_colunas.append('Não')
        else:
            # Se não valor colunas 36 a 38
            valores_colunas.append('')
            valores_colunas.append('')
            valores_colunas.append('Não')
            

        if sistema.ente_federado:
            # Coluna 39
            valores_colunas.append(sistema.ente_federado.populacao)
            
            # Coluna 40
            valores_colunas.append(sistema.ente_federado.idh)

            # Coluna 41
            valores_colunas.append(sistema.ente_federado.pib)
            
            # Coluna 42
            valores_colunas.append(sistema.ente_federado.mandatario)

            # Coluna 43
            if sistema.gestor_cultura:
                valores_colunas.append(sistema.gestor_cultura.nome)
            else:
                valores_colunas.append('')
            
            # Coluna 44
            valores_colunas.append(get_email_municipio(sistema))
            
            # Coluna 45
            valores_colunas.append(sistema.sede.telefone_um)
            
            # Coluna 46
            valores_colunas.append(sistema.sede.endereco)
            
            # Coluna 47
            valores_colunas.append(sistema.sede.cep)
       
        # gera linhas e colunas na planilha
        for c, elem in enumerate(valores_colunas):
            planilha.write(i, c, valores_colunas[c])

    ultima_linha = i

    return ultima_linha

def get_email_municipio(sistema):
    result = ''
    if sistema.ente_federado:
        cid = Cidade.objects.filter(nome_municipio=sistema.ente_federado.nome)
        if len(cid) > 0:
            mun = cid[0].municipio_set.all()
            if len(mun) > 0:
                if mun[0].email_institucional_prefeito:
                    result = str(mun[0].email_institucional_prefeito)
    return result