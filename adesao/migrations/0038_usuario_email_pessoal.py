# Generated by Django 2.0.8 on 2019-03-29 17:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adesao', '0037_merge_20190320_1154'),
    ]

    operations = [
        migrations.AddField(
            model_name='usuario',
            name='email_pessoal',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
    ]
