# Generated by Django 2.0.8 on 2019-02-21 17:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gestao', '0008_merge_20181010_1518'),
        ('planotrabalho', '0015_auto_20190218_1811'),
    ]

    def migrar_diligencia_para_arquivo(apps, schema_editor):
        Componente = apps.get_model('planotrabalho', 'Componente')
        ArquivoComponente2 = apps.get_model(
            'planotrabalho', 'ArquivoComponente2')

        for componente in Componente.objects.all():
            componente.diligencia_arquivo = componente.diligencia
            componente.save()

    operations = [
        migrations.AddField(
            model_name='arquivocomponente2',
            name='diligencia_arquivo',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='gestao.DiligenciaSimples'),
        ),
        migrations.RunPython(migrar_diligencia_para_arquivo),
    ]
