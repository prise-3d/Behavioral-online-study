# Generated by Django 3.2.12 on 2022-02-05 23:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('expe', '0009_alter_classicalexperimentprogress_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='classicalexperimentprogress',
            name='id',
            field=models.AutoField(editable=False, primary_key=True, serialize=False, unique=True),
        ),
    ]
