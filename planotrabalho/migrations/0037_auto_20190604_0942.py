# Generated by Django 2.0.8 on 2019-06-04 12:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('planotrabalho', '0036_auto_20190531_1927'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='historicalplanodecultura',
            name='decenal',
        ),
        migrations.RemoveField(
            model_name='planodecultura',
            name='decenal',
        ),
        migrations.AlterField(
            model_name='historicalplanodecultura',
            name='local_monitoramento',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Local de Monitoramento'),
        ),
        migrations.AlterField(
            model_name='planodecultura',
            name='local_monitoramento',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Local de Monitoramento'),
        ),
    ]