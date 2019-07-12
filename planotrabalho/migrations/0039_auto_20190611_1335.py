# Generated by Django 2.0.8 on 2019-06-11 16:35

from django.db import migrations

def migra_plano(apps, schema_editor):
    Componente = apps.get_model('planotrabalho', 'Componente')
    PlanoDeCultura = apps.get_model('planotrabalho', 'PlanoDeCultura')

    PLANO = 4
    for componente in Componente.objects.filter(tipo=PLANO):
        plano = PlanoDeCultura()
        plano.componente_ptr = componente
        plano.save()

        componente.planodecultura = plano
        componente.save()


class Migration(migrations.Migration):

    dependencies = [
        ('planotrabalho', '0038_auto_20190604_1439'),
    ]

    operations = [
        migrations.RunPython(migra_plano)
    ]