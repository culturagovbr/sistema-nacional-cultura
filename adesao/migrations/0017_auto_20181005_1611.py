# Generated by Django 2.0.8 on 2018-10-05 19:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adesao', '0016_auto_20181005_1608'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sede',
            name='endereco',
            field=models.TextField(),
        ),
    ]
