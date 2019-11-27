# Generated by Django 2.0.8 on 2019-05-10 20:08

from django.db import migrations

def mudar_situacao_componentes(apps, schema_editor):
	Componente = apps.get_model('planotrabalho', 'Componente')

	for componente in Componente.objects.exclude(arquivo=None).filter(situacao=0):
		componente.situacao = 1
		componente.save()

class Migration(migrations.Migration):

    dependencies = [
        ('planotrabalho', '0033_auto_20190507_1636'),
    ]

    operations = [
        migrations.RunPython(mudar_situacao_componentes)  
    ]
