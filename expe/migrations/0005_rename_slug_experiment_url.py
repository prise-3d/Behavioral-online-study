# Generated by Django 3.2.12 on 2022-02-03 14:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('expe', '0004_auto_20220203_1444'),
    ]

    operations = [
        migrations.RenameField(
            model_name='experiment',
            old_name='slug',
            new_name='url',
        ),
    ]
