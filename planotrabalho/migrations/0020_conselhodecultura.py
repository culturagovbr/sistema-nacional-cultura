# Generated by Django 2.0.8 on 2019-03-08 19:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('planotrabalho', '0019_arquivocomponente2_data_publicacao_aux'),
    ]

    operations = [
        migrations.CreateModel(
            name='ConselhoDeCultura',
            fields=[
                ('componente_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='planotrabalho.Componente')),
                ('lei', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='conselhos', to='planotrabalho.ArquivoComponente2')),
            ],
            bases=('planotrabalho.componente',),
        ),
    ]
