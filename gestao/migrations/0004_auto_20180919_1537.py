# Generated by Django 2.0.8 on 2018-09-19 18:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestao', '0003_auto_20180919_1413'),
    ]

    operations = [
        migrations.AlterField(
            model_name='diligencia',
            name='classificacao_arquivo',
            field=models.IntegerField(blank=True, choices=[(0, 'Em preenchimento'), (1, 'Avaliando anexo'), (2, 'Concluída'), (3, 'Arquivo aprovado com ressalvas'), (4, 'Arquivo danificado'), (5, 'Arquivo incompleto'), (6, 'Arquivo incorreto')], null=True),
        ),
    ]