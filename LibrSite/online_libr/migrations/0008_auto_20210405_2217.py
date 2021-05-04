# Generated by Django 3.1.7 on 2021-04-05 19:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('online_libr', '0007_auto_20210402_1926'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='description',
            field=models.CharField(blank=True, default='', max_length=500),
        ),
        migrations.AddField(
            model_name='book',
            name='rating',
            field=models.IntegerField(default=0, editable=False),
        ),
    ]