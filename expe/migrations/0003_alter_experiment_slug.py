# Generated by Django 3.2.12 on 2022-02-03 14:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('expe', '0002_remove_experiment_author'),
    ]

    operations = [
        migrations.AlterField(
            model_name='experiment',
            name='slug',
            field=models.SlugField(blank=True, max_length=255, unique=True),
        ),
    ]
