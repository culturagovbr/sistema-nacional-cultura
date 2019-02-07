# Generated by Django 2.0.8 on 2019-02-05 17:08

import datetime
from django.db import migrations, models
import django.db.models.deletion
import planotrabalho.models


class Migration(migrations.Migration):

    dependencies = [
        ('planotrabalho', '0012_auto_20181218_1436'),
    ]

    def cria_arquivo_componente(apps, schema_editor):
        Componente = apps.get_model('planotrabalho', 'Componente')
        ArquivoComponente2 = apps.get_model(
            'planotrabalho', 'ArquivoComponente2')

        for componente in Componente.objects.all().order_by('id'):
            arquivo = ArquivoComponente2()
            arquivo.id = componente.id
            arquivo.arquivo = componente.arquivo
            arquivo.situacao = componente.situacao
            arquivo.data_envio = componente.data_envio
            arquivo.save()

            componente.arquivo_temp = arquivo
            componente.save()

    operations = [
        migrations.CreateModel(
            name='ArquivoComponente2',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('arquivo', models.FileField(blank=True, null=True, upload_to=planotrabalho.models.upload_to)),
                ('situacao', models.IntegerField(choices=[(0, 'Em preenchimento'), (1, 'Avaliando anexo'), (2, 'Concluída'), (3, 'Arquivo aprovado com ressalvas'), (4, 'Arquivo danificado'), (5, 'Arquivo incompleto'), (6, 'Arquivo incorreto')], default=0, verbose_name='Situação do Arquivo')),
                ('data_envio', models.DateField(default=datetime.date.today)),
            ],
        ),
        migrations.AddField(
            model_name='componente',
            name='arquivo_temp',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to='planotrabalho.ArquivoComponente2')
        ),
        migrations.RunPython(cria_arquivo_componente),
        migrations.RemoveField(
            model_name='componente',
            name='data_envio',
        ),
        migrations.RemoveField(
            model_name='componente',
            name='situacao',
        ),
        migrations.RemoveField(
            model_name='componente',
            name='arquivo',
        ),
        migrations.RenameField(
            model_name='componente',
            old_name='arquivo_temp',
            new_name='arquivo'
        ),
        migrations.AddField(
            model_name='fundodecultura',
            name='regulamentacao',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='fundos',
                to='planotrabalho.ArquivoComponente2'),
        ),
    ]
