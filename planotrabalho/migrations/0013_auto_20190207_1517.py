# Generated by Django 2.0.8 on 2019-02-07 17:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('planotrabalho', '0012_auto_20181218_1436'),
    ]

    operations = [
        migrations.AlterField(
            model_name='conselheiro',
            name='conselho',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='planotrabalho.Componente'),
        ),
    ]
