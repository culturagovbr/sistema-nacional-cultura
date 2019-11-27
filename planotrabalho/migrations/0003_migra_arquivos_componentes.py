# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def migra_arquivo_criacao_sistema(apps, schema_editor):
    """ Migra arquivo do componente do field 'lei_sistema_cultura'
    para 'arquivo' """

    CriacaoSistema = apps.get_model("planotrabalho", "CriacaoSistema")
    for sistema in CriacaoSistema.objects.all():
        try:
            file = sistema.lei_sistema_cultura.file
            file_name = file.name.split('/')[-1]
            sistema.arquivo.save(file_name, file)
            file.close()
        except ValueError:
            """ Sem file associado """
            pass


def migra_arquivo_orgao_gestor(apps, schema_editor):
    """ Migra arquivo do componente do field 'relatorio_atividade_secretaria'
    para 'arquivo' """

    OrgaoGestor = apps.get_model("planotrabalho", "OrgaoGestor")
    for orgao in OrgaoGestor.objects.all():
        try:
            file = orgao.relatorio_atividade_secretaria.file
            file_name = file.name.split('/')[-1]
            orgao.arquivo.save(file_name, file)
            file.close()
        except ValueError:
            """ Sem file associado """
            pass


def migra_arquivo_conselho_cultural(apps, schema_editor):
    """ Migra arquivo do componente do field 'ata_regimento_aprovado'
    para 'arquivo' """

    ConselhoCultural = apps.get_model("planotrabalho", "ConselhoCultural")
    for conselho in ConselhoCultural.objects.all():
        try:
            file = conselho.ata_regimento_aprovado.file
            file_name = file.name.split('/')[-1]
            conselho.arquivo.save(file_name, file)
            file.close()
        except ValueError:
            """ Sem file associado """
            pass


def migra_arquivo_fundo_cultura(apps, schema_editor):
    """ Migra arquivo do componente do field 'lei_fundo_cultura'
    para 'arquivo' """

    FundoCultura = apps.get_model("planotrabalho", "FundoCultura")
    for fundo in FundoCultura.objects.all():
        try:
            file = fundo.lei_fundo_cultura.file
            file_name = file.name.split('/')[-1]
            fundo.arquivo.save(file_name, file)
            file.close()
        except ValueError:
            """ Sem file associado """
            pass


def migra_arquivo_plano_cultura(apps, schema_editor):
    """ Migra arquivo do componente do field 'lei_plano_cultura'
    para 'arquivo' """

    PlanoCultura = apps.get_model("planotrabalho", "PlanoCultura")
    for plano in PlanoCultura.objects.all():
        try:
            file = plano.lei_plano_cultura.file
            file_name = file.name.split('/')[-1]
            plano.arquivo.save(file_name, file)
            file.close()
        except ValueError:
            """ Sem file associado """
            pass


class Migration(migrations.Migration):

    dependencies = [
        ('planotrabalho', '0002_newfields'),
    ]

    operations = [
        migrations.RunPython(migra_arquivo_criacao_sistema),
        migrations.RunPython(migra_arquivo_orgao_gestor),
        migrations.RunPython(migra_arquivo_conselho_cultural),
        migrations.RunPython(migra_arquivo_fundo_cultura),
        migrations.RunPython(migra_arquivo_plano_cultura),
    ]
