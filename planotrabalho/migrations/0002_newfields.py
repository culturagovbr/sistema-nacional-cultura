# Generated by Django 2.0.4 on 2018-05-23 14:23

import datetime
from django.db import migrations, models
import django.db.models.deletion
import planotrabalho.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('planotrabalho', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='planocultura',
            old_name='situacao_lei_plano',
            new_name='situacao',
        ),
        migrations.AddField(
            model_name='planocultura',
            name='arquivo',
            field=models.FileField(blank=True, null=True, upload_to=planotrabalho.models.upload_to_componente)
        ),
        migrations.AddField(
            model_name='planocultura',
            name='data_envio',
            field=models.DateField(default=datetime.date.today)
        ),
        migrations.RenameField(
            model_name='orgaogestor',
            old_name='situacao_relatorio_secretaria',
            new_name='situacao',
        ),
        migrations.AddField(
            model_name='orgaogestor',
            name='arquivo',
            field=models.FileField(blank=True, null=True, upload_to=planotrabalho.models.upload_to_componente)
        ),
        migrations.AddField(
            model_name='orgaogestor',
            name='data_envio',
            field=models.DateField(default=datetime.date.today)
        ),
        migrations.RenameField(
            model_name='fundocultura',
            old_name='situacao_lei_plano',
            new_name='situacao',
        ),
        migrations.AddField(
            model_name='fundocultura',
            name='arquivo',
            field=models.FileField(blank=True, null=True, upload_to=planotrabalho.models.upload_to_componente)
            ),
        migrations.AddField(
            model_name='fundocultura',
            name='data_envio',
            field=models.DateField(default=datetime.date.today)
        ),
        migrations.RenameField(
            model_name='criacaosistema',
            old_name='situacao_lei_sistema',
            new_name='situacao',
        ),
        migrations.AddField(
            model_name='criacaosistema',
            name='arquivo',
            field=models.FileField(blank=True, null=True, upload_to=planotrabalho.models.upload_to_componente)
        ),
        migrations.AddField(
            model_name='criacaosistema',
            name='data_envio',
            field=models.DateField(default=datetime.date.today)
        ),
        migrations.RenameField(
            model_name='conselhocultural',
            old_name='situacao_ata',
            new_name='situacao',
        ),
        migrations.AddField(
            model_name='conselhocultural',
            name='arquivo',
            field=models.FileField(blank=True, null=True, upload_to=planotrabalho.models.upload_to_componente)
        ),
        migrations.AddField(
            model_name='conselhocultural',
            name='data_envio',
            field=models.DateField(default=datetime.date.today)
        ),
        # migrations.AddField(
        #     model_name='conselheiro',
        #     name='conselho',
        #     field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='planotrabalho.ConselhoCultural'),
        # ),
    ]
