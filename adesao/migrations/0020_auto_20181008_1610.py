# Generated by Django 2.0.8 on 2018-10-08 19:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adesao', '0018_remove_sistemacultura_localizacao'),
    ]

    operations = [
        migrations.AlterField(
            model_name='funcionario',
            name='rg',
            field=models.CharField(max_length=50, verbose_name='RG'),
        ),
        migrations.AlterField(
            model_name='funcionario',
            name='telefone_dois',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='funcionario',
            name='telefone_tres',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='funcionario',
            name='telefone_um',
            field=models.CharField(max_length=50),
        ),
    ]
