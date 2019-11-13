import csv
import json

with open("fixtures/entes.csv", encoding="ISO-8859-1") as file:
    i = csv.DictReader(file)
    data = []
    pk = 20563

    for df in i:
        ente = {}
        ente['model'] = "adesao.entefederado"
        ente['pk'] = pk
        ente['fields'] = {}
        pk += 1

        ente['fields']['cod_ibge'] = int(df['CODIGO [-]'])
        ente['fields']['nome'] = df['NOME_MUNICIPIO [-]']
        ente['fields']['gentilico'] = df['GENTILICO [-]']
        ente['fields']['mandatario'] = df['PREFEITO [2017]']
        ente['fields']['territorio'] = int(df['AREA - AREA [2017]'])
        ente['fields']['populacao'] = int(df['POPESTIMADA - POPESTIMADA [2018]'])

        if df['DENSIDADE - DENSIDADE [2010]'] == '-':
            ente['fields']['densidade'] = None
        else:
            ente['fields']['densidade'] = float(df['DENSIDADE - DENSIDADE [2010]'])

        if df['IDHM [2010]'] == '-':
            ente['fields']['idh'] = None
        else:
            ente['fields']['idh'] = float(df['IDHM [2010]'])/1000
        
        if df['RECEITAS - REAL_MIL [2017]'] == "Não informado":
            ente['fields']['receita'] = None
        else:
            ente['fields']['receita'] = int(df['RECEITAS - REAL_MIL [2017]'].split('.')[0])

        if df['DESPESAS - REAL_MIL [2017]'] == "Não informado":
            ente['fields']['despesas'] = None
        else:
            ente['fields']['despesas'] = int(df['DESPESAS - REAL_MIL [2017]'].split('.')[0])

        ente['fields']['pib'] = float(df['PIB - REAL [2016]'])

        data.append(ente)

with open('fixtures/ibge.json', 'w') as outfile:
    json.dump(data, outfile)