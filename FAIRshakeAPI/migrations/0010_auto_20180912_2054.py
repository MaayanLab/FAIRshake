# Generated by Django 2.0.7 on 2018-09-12 20:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FAIRshakeAPI', '0009_auto_20180912_2051'),
    ]

    operations = [
        migrations.AlterField(
            model_name='digitalobject',
            name='slug',
            field=models.CharField(max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='metric',
            name='slug',
            field=models.CharField(max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='slug',
            field=models.CharField(max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='rubric',
            name='slug',
            field=models.CharField(max_length=255, unique=True),
        ),
    ]
