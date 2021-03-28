# Generated by Django 3.1.7 on 2021-03-28 21:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('online_libr', '0005_auto_20210328_2057'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='date',
            field=models.DateField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='review',
            name='rating',
            field=models.IntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10)], default=10),
        ),
        migrations.AddConstraint(
            model_name='review',
            constraint=models.UniqueConstraint(fields=('user', 'book'), name='unique_review'),
        ),
    ]