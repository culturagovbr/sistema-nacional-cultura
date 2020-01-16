from adesao.models import SistemaCultura
from django.db.models import Q
from django.db import connection


def preenche_planilha(planilha, codigos):
    planilha.write(0, 0, "Ente federado")
    planilha.write(0, 1, "UF")
    planilha.write(0, 2, "Data da adesão")

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

        planilha.write(i, 0, nome)
        planilha.write(i, 1, sistema.ente_federado.sigla)
        planilha.write(i, 2, data_publicacao_acordo)

        ultima_linha = i

    return ultima_linha
