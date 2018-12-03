# Generated by Django 2.0.8 on 2018-11-30 18:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('planotrabalho', '0008_componente_data_publicacao'),
    ]

    operations = [
        migrations.CreateModel(
            name='FundoDeCultura',
            fields=[
                ('componente_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='planotrabalho.Componente')),
                ('cnpj', models.CharField(blank=True, default=None, max_length=18, null=True, verbose_name='CNPJ')),
            ],
            options={
                'abstract': False,
            },
            bases=('planotrabalho.componente',),
        ),
    ]
