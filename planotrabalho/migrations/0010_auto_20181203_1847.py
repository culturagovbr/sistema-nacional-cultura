from django.db import migrations
from adesao.models import SistemaCultura, Municipio, Usuario
from planotrabalho.models import FundoDeCultura
from django.core.exceptions import ObjectDoesNotExist


def cria_fundo_de_cultura(apps, schema_editor):

	for municipio in Municipio.objects.exclude(usuario__plano_trabalho__fundo_cultura=None):
		fundo_antigo = municipio.usuario.plano_trabalho.fundo_cultura

		if municipio.cidade:
			sistemas = SistemaCultura.sistema.filter(ente_federado__nome=municipio.cidade.nome_municipio)
			codigo_ibge = str(municipio.cidade.codigo_ibge)
		else:
			sistemas = SistemaCultura.sistema.filter(ente_federado__nome=municipio.estado.nome_uf)
			codigo_ibge = str(municipio.estado.codigo_ibge)

		if sistemas.count() > 1:
			for sistema in sistemas:
				if codigo_ibge in str(sistema.ente_federado.cod_ibge):
					sistema_fundo = sistema
					break
		elif sistemas.count() == 1:
			sistema_fundo = sistemas[0]
		else:
			print("ente: ", codigo_ibge, "\n")
			continue

		FUNDO_CULTURA = 2
		fundo_novo = FundoDeCultura.objects.create(tipo=2, arquivo=fundo_antigo.arquivo,
		situacao=fundo_antigo.situacao.id, data_envio=fundo_antigo.data_envio,
		data_publicacao=fundo_antigo.data_publicacao, cnpj=fundo_antigo.cnpj_fundo_cultura)
		sistema_fundo.fundo_cultura = fundo_novo
		sistema_fundo.save()


class Migration(migrations.Migration):

	dependencies = [
		('planotrabalho', '0009_fundodecultura'),
	]

	operations = [
		migrations.RunPython(cria_fundo_de_cultura)
	]