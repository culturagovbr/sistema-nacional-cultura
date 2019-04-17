# Generated by Django 2.0.8 on 2019-03-01 15:04

from django.db import migrations, models

def copia_data_publicacao(apps, schema_editor):
    Componente = apps.get_model('planotrabalho', 'Componente')

    for componente in Componente.objects.all():
        componente.data_publicacao_aux = componente.data_publicacao
        componente.save()


class Migration(migrations.Migration):

    dependencies = [
        ('planotrabalho', '0018_auto_20190226_1419'),
    ]

    operations = [
        migrations.AddField(
            model_name='arquivocomponente2',
            name='data_publicacao_aux',
            field=models.DateField(blank=True, null=True, verbose_name='Data de Publicação do Arquivo do Componente'),
        ),
        migrations.RunPython(copia_data_publicacao),
        migrations.RemoveField(
            model_name='componente',
            name='data_publicacao',
        ),
        migrations.RenameField(
            model_name='arquivocomponente2',
            old_name='data_publicacao_aux',
            new_name='data_publicacao',
        ),
    ]