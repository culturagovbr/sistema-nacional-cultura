# Generated by Django 2.0.8 on 2018-09-27 12:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gestao', '0005_auto_20180927_0955'),
        ('planotrabalho', '0006_auto_20180924_1449'),
    ]

    operations = [
        migrations.AddField(
            model_name='componente',
            name='diligencia',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='componente', to='gestao.DiligenciaSimples'),
        ),
    ]
