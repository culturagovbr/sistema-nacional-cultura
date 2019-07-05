# Generated by Django 2.0.8 on 2019-05-31 22:27

import datetime
from django.conf import settings
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import simple_history.models


class Migration(migrations.Migration):

    dependencies = [
        ('gestao', '0011_contato'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('planotrabalho', '0035_merge_20190522_1258'),
    ]

    operations = [
        migrations.CreateModel(
            name='HistoricalPlanoDeCultura',
            fields=[
                ('componente_ptr', models.ForeignKey(auto_created=True, blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, parent_link=True, related_name='+', to='planotrabalho.Componente')),
                ('arquivocomponente2_ptr', models.ForeignKey(auto_created=True, blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, parent_link=True, related_name='+', to='planotrabalho.ArquivoComponente2')),
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('arquivo', models.TextField(blank=True, max_length=100, null=True)),
                ('situacao', models.IntegerField(choices=[(0, 'Em preenchimento'), (1, 'Avaliando anexo'), (2, 'Concluída'), (3, 'Arquivo aprovado com ressalvas'), (4, 'Arquivo danificado'), (5, 'Arquivo incompleto'), (6, 'Arquivo incorreto')], default=0, verbose_name='Situação do Arquivo')),
                ('data_envio', models.DateField(default=datetime.date.today)),
                ('data_publicacao', models.DateField(blank=True, null=True, verbose_name='Data de Publicação do Arquivo do Componente')),
                ('tipo', models.IntegerField(choices=[(0, 'Lei Sistema'), (1, 'Órgão Gestor'), (2, 'Fundo Cultura'), (3, 'Conselho Cultural'), (4, 'Plano Cultura')], default=0)),
                ('exclusivo_cultura', models.BooleanField(default=False)),
                ('anexo_na_lei', models.BooleanField(default=False)),
                ('metas_na_lei', models.BooleanField(default=False)),
                ('ultimo_ano_vigencia', models.IntegerField(blank=True, null=True)),
                ('decenal', models.BooleanField(default=False)),
                ('periodicidade', models.CharField(blank=True, max_length=100, null=True)),
                ('local_monitoramento', models.CharField(blank=True, max_length=100, null=True, verbose_name='Local de Monitoramente')),
                ('ano_curso', models.IntegerField(blank=True, null=True)),
                ('tipo_curso', models.IntegerField(blank=True, choices=[(0, 'Oficina'), (1, 'Palestra'), (2, 'Seminário'), (3, 'Pós-Graduação'), (4, 'Especialização'), (5, 'Aperfeiçoamento'), (6, 'Extensão')], null=True, verbose_name='Tipo do Curso')),
                ('esfera_federacao_curso', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=1), blank=True, null=True, size=3)),
                ('tipo_oficina', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=1), blank=True, null=True, size=7)),
                ('perfil_participante', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=1), blank=True, null=True, size=3)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('anexo', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='planotrabalho.ArquivoComponente2')),
                ('diligencia', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='gestao.DiligenciaSimples')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('metas', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='planotrabalho.ArquivoComponente2')),
            ],
            options={
                'verbose_name': 'historical plano de cultura',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='PlanoDeCultura',
            fields=[
                ('componente_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='planotrabalho.Componente')),
                ('exclusivo_cultura', models.BooleanField(default=False)),
                ('anexo_na_lei', models.BooleanField(default=False)),
                ('metas_na_lei', models.BooleanField(default=False)),
                ('ultimo_ano_vigencia', models.IntegerField(blank=True, null=True)),
                ('decenal', models.BooleanField(default=False)),
                ('periodicidade', models.CharField(blank=True, max_length=100, null=True)),
                ('local_monitoramento', models.CharField(blank=True, max_length=100, null=True, verbose_name='Local de Monitoramente')),
                ('ano_curso', models.IntegerField(blank=True, null=True)),
                ('tipo_curso', models.IntegerField(blank=True, choices=[(0, 'Oficina'), (1, 'Palestra'), (2, 'Seminário'), (3, 'Pós-Graduação'), (4, 'Especialização'), (5, 'Aperfeiçoamento'), (6, 'Extensão')], null=True, verbose_name='Tipo do Curso')),
                ('esfera_federacao_curso', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=1), blank=True, null=True, size=3)),
                ('tipo_oficina', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=1), blank=True, null=True, size=7)),
                ('perfil_participante', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=1), blank=True, null=True, size=3)),
                ('anexo', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='anexo_plano', to='planotrabalho.ArquivoComponente2')),
                ('metas', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='metas_plano', to='planotrabalho.ArquivoComponente2')),
            ],
            bases=('planotrabalho.componente',),
        ),
    ]
