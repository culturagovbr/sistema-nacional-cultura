# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Conselheiro',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('nome', models.CharField(max_length=100)),
                ('segmento', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254)),
                ('situacao', models.CharField(max_length=1, default=1, blank=True, null=True, choices=[('1', 'Habilitado'), ('0', 'Desabilitado')])),
                ('data_cadastro', models.DateField(blank=True, null=True)),
                ('data_situacao', models.DateField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ConselhoCultural',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('ata_regimento_aprovado', models.FileField(max_length=255, upload_to='regimentos', blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='CriacaoSistema',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('minuta_projeto_lei', models.FileField(max_length=255, upload_to='minuta_lei', blank=True, null=True)),
                ('lei_sistema_cultura', models.FileField(max_length=255, upload_to='leis_sistema_cultura', blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='FundoCultura',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('cnpj_fundo_cultura', models.CharField(max_length=18, default=None, blank=True, null=True, verbose_name='CNPJ')),
                ('lei_fundo_cultura', models.FileField(max_length=255, upload_to='lei_fundo_cultura', blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='OrgaoGestor',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('relatorio_atividade_secretaria', models.FileField(max_length=255, upload_to='relatorio_atividades', blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='PlanoCultura',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('relatorio_diretrizes_aprovadas', models.FileField(max_length=255, upload_to='relatorio_diretrizes', blank=True, null=True)),
                ('minuta_preparada', models.FileField(max_length=255, upload_to='minuta_preparada', blank=True, null=True)),
                ('ata_reuniao_aprovacao_plano', models.FileField(max_length=255, upload_to='ata_aprovacao_plano', blank=True, null=True)),
                ('ata_votacao_projeto_lei', models.FileField(max_length=255, upload_to='ata_votacao_lei', blank=True, null=True)),
                ('lei_plano_cultura', models.FileField(max_length=255, upload_to='lei_plano_cultura', blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='PlanoTrabalho',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('conselho_cultural', models.OneToOneField(blank=True, null=True, to='planotrabalho.ConselhoCultural', on_delete=django.db.models.deletion.CASCADE)),
                ('criacao_sistema', models.OneToOneField(blank=True, null=True, to='planotrabalho.CriacaoSistema', on_delete=django.db.models.deletion.CASCADE)),
                ('fundo_cultura', models.OneToOneField(blank=True, null=True, to='planotrabalho.FundoCultura', on_delete=django.db.models.deletion.CASCADE)),
                ('orgao_gestor', models.OneToOneField(blank=True, null=True, to='planotrabalho.OrgaoGestor', on_delete=django.db.models.deletion.CASCADE)),
                ('plano_cultura', models.OneToOneField(blank=True, null=True, to='planotrabalho.PlanoCultura', on_delete=django.db.models.deletion.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='SituacoesArquivoPlano',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('descricao', models.CharField(max_length=75)),
            ],
        ),
        migrations.AddField(
            model_name='planocultura',
            name='situacao_lei_plano',
            field=models.ForeignKey(to='planotrabalho.SituacoesArquivoPlano', on_delete=django.db.models.deletion.CASCADE),
        ),
        migrations.AddField(
            model_name='orgaogestor',
            name='situacao_relatorio_secretaria',
            field=models.ForeignKey(to='planotrabalho.SituacoesArquivoPlano', on_delete=django.db.models.deletion.CASCADE),
        ),
        migrations.AddField(
            model_name='fundocultura',
            name='situacao_lei_plano',
            field=models.ForeignKey(to='planotrabalho.SituacoesArquivoPlano', on_delete=django.db.models.deletion.CASCADE),
        ),
        migrations.AddField(
            model_name='criacaosistema',
            name='situacao_lei_sistema',
            field=models.ForeignKey(to='planotrabalho.SituacoesArquivoPlano', on_delete=django.db.models.deletion.CASCADE),
        ),
        migrations.AddField(
            model_name='conselhocultural',
            name='situacao_ata',
            field=models.ForeignKey(to='planotrabalho.SituacoesArquivoPlano', on_delete=django.db.models.deletion.CASCADE),
        ),
        migrations.AddField(
            model_name='conselheiro',
            name='conselho',
            field=models.ForeignKey(to='planotrabalho.ConselhoCultural', on_delete=django.db.models.deletion.CASCADE),
        ),
    ]
