# Generated by Django 4.2.6 on 2023-11-01 04:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('collection', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='period',
            name='name',
            field=models.CharField(max_length=200, unique=True),
        ),
    ]
