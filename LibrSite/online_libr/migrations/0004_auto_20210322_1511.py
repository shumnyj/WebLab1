# Generated by Django 3.1.7 on 2021-03-22 13:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('online_libr', '0003_auto_20210321_1955'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='date',
            field=models.DateField(auto_now_add=True),
        ),
    ]
