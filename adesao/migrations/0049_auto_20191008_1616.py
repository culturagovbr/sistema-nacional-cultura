# Generated by Django 2.0.8 on 2019-10-08 19:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('adesao', '0048_auto_20190730_1955'),
    ]

    operations = [
        migrations.AddField(
            model_name='funcionario',
            name='bairro',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='funcionario',
            name='cep',
            field=models.CharField(max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='funcionario',
            name='complemento',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='funcionario',
            name='endereco',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='funcionario',
            name='estado_endereco',
            field=models.ForeignKey(choices=[(12, 'AC'), (27, 'AL'), (13, 'AM'), (16, 'AP'), (29, 'BA'), (23, 'CE'), (53, 'DF'), (32, 'ES'), (52, 'GO'), (21, 'MA'), (31, 'MG'), (50, 'MS'), (51, 'MT'), (15, 'PA'), (25, 'PB'), (26, 'PE'), (22, 'PI'), (41, 'PR'), (33, 'RJ'), (24, 'RN'), (11, 'RO'), (14, 'RR'), (43, 'RS'), (42, 'SC'), (28, 'SE'), (35, 'SP'), (17, 'TO')], null=True, on_delete=django.db.models.deletion.CASCADE, related_name='funcionario_estado_endereco', to='adesao.Uf'),
        ),
    ]
