# Generated by Django 2.2.14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myApp', '0003_auto_20220805_1225'),
    ]

    operations = [
        migrations.AddField(
            model_name='jobinfo',
            name='dist',
            field=models.CharField(default='', max_length=255, verbose_name='行政区'),
        ),
    ]