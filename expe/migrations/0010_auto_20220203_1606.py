# Generated by Django 3.2.12 on 2022-02-03 16:06

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('expe', '0009_alter_userexperiment_sessions'),
    ]

    operations = [
        migrations.AlterField(
            model_name='examplepage',
            name='template',
            field=models.CharField(choices=[('first_example.html', 'first_example.html')], help_text='You can add templates into: expe/templates/examples', max_length=255),
        ),
        migrations.AlterField(
            model_name='userexperiment',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        ),
    ]
