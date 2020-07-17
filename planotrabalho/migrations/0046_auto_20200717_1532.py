# Generated by Django 2.0.8 on 2020-07-17 18:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planotrabalho', '0045_auto_20200708_1445'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fundodecultura',
            name='banco',
            field=models.CharField(blank=True, choices=[(0, 'Selecione o Banco'), (1, '001 - BANCODO BRASIL S.A'), (2, '104 - CAIXA ECONOMICA FEDERAL')], max_length=20, null=True, verbose_name='Banco'),
        ),
        migrations.AlterField(
            model_name='historicalfundodecultura',
            name='banco',
            field=models.CharField(blank=True, choices=[(0, 'Selecione o Banco'), (1, '001 - BANCODO BRASIL S.A'), (2, '104 - CAIXA ECONOMICA FEDERAL')], max_length=20, null=True, verbose_name='Banco'),
        ),
        migrations.AlterField(
            model_name='historicalorgaogestor2',
            name='banco',
            field=models.CharField(blank=True, choices=[(0, 'Selecione o Banco'), (1, '001 - BANCODO BRASIL S.A'), (2, '104 - CAIXA ECONOMICA FEDERAL')], max_length=20, null=True, verbose_name='Banco'),
        ),
        migrations.AlterField(
            model_name='orgaogestor2',
            name='banco',
            field=models.CharField(blank=True, choices=[(0, 'Selecione o Banco'), (1, '001 - BANCODO BRASIL S.A'), (2, '104 - CAIXA ECONOMICA FEDERAL')], max_length=20, null=True, verbose_name='Banco'),
        ),
    ]
