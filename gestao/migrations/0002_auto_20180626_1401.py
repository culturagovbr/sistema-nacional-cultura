# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestao', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='diligencia',
            name='tipo_diligencia',
            field=models.CharField(choices=[('geral', 'Geral'), ('componente', 'Específica')], max_length=10),
        ),
    ]
