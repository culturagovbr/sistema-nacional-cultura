# Generated by Django 2.0.8 on 2020-07-08 13:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('planotrabalho', '0041_auto_20200705_1922'),
    ]

    operations = [
        migrations.RenameField(
            model_name='historicalorgaogestor2',
            old_name='comprovante_cnpj',
            new_name='comprovante',
        ),
        migrations.RenameField(
            model_name='orgaogestor2',
            old_name='comprovante_cnpj',
            new_name='comprovante',
        ),
    ]
