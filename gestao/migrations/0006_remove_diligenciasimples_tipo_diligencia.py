# Generated by Django 2.0.8 on 2018-10-01 17:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gestao', '0005_diligenciasimples'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='diligenciasimples',
            name='tipo_diligencia',
        ),
    ]
