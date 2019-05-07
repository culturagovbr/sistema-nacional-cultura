# Generated by Django 2.0.8 on 2019-05-07 19:36

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import simple_history.models


class Migration(migrations.Migration):

    dependencies = [
        ('gestao', '0010_historicaldiligenciasimples_arquivo_url'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('planotrabalho', '0031_merge_20190422_1653'),
    ]

    operations = [
        migrations.CreateModel(
            name='HistoricalOrgaoGestor2',
            fields=[
                ('componente_ptr', models.ForeignKey(auto_created=True, blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, parent_link=True, related_name='+', to='planotrabalho.Componente')),
                ('arquivocomponente2_ptr', models.ForeignKey(auto_created=True, blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, parent_link=True, related_name='+', to='planotrabalho.ArquivoComponente2')),
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('arquivo', models.TextField(blank=True, max_length=100, null=True)),
                ('situacao', models.IntegerField(choices=[(0, 'Em preenchimento'), (1, 'Avaliando anexo'), (2, 'Concluída'), (3, 'Arquivo aprovado com ressalvas'), (4, 'Arquivo danificado'), (5, 'Arquivo incompleto'), (6, 'Arquivo incorreto')], default=0, verbose_name='Situação do Arquivo')),
                ('data_envio', models.DateField(default=datetime.date.today)),
                ('data_publicacao', models.DateField(blank=True, null=True, verbose_name='Data de Publicação do Arquivo do Componente')),
                ('tipo', models.IntegerField(choices=[(0, 'Lei Sistema'), (1, 'Órgão Gestor'), (2, 'Fundo Cultura'), (3, 'Conselho Cultural'), (4, 'Plano Cultura')], default=0)),
                ('perfil', models.IntegerField(blank=True, choices=[(0, 'Secretaria exclusiva de cultura'), (1, 'Secretaria em conjunto com outras políticas'), (2, 'Órgão da administração indireta'), (3, 'Setor subordinado à chefia do Executivo'), (4, 'Setor subordinado à outra secretaria'), (5, 'Não possui estrutura')], null=True)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('diligencia', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='gestao.DiligenciaSimples')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical orgao gestor2',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='OrgaoGestor2',
            fields=[
                ('componente_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='planotrabalho.Componente')),
                ('perfil', models.IntegerField(blank=True, choices=[(0, 'Secretaria exclusiva de cultura'), (1, 'Secretaria em conjunto com outras políticas'), (2, 'Órgão da administração indireta'), (3, 'Setor subordinado à chefia do Executivo'), (4, 'Setor subordinado à outra secretaria'), (5, 'Não possui estrutura')], null=True)),
            ],
            bases=('planotrabalho.componente',),
        ),
    ]
