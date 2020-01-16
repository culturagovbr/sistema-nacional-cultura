from adesao.models import SistemaCultura


def preenche_planilha(planilha, ids):
    planilha.write(0, 0, "Ente federado")
    planilha.write(0, 1, "UF")
    planilha.write(0, 2, "Data da adesão")

    ultima_linha = 0
    sistema = SistemaCultura.sistema.filter(id__in=ids).filter(
        ente_federado__isnull=False)

    for i, sistema in enumerate(sistema, start=1):
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
