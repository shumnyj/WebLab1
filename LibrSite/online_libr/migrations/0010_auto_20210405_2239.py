# Generated by Django 3.1.7 on 2021-04-05 19:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('online_libr', '0009_auto_20210405_2226'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='readstatus',
            options={'ordering': ['status']},
        ),
    ]
