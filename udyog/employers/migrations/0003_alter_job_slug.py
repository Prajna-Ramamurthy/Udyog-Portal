# Generated by Django 4.2.5 on 2023-11-17 05:20

import autoslug.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('employers', '0002_jobreport'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job',
            name='slug',
            field=autoslug.fields.AutoSlugField(editable=False, null=True, populate_from='title'),
        ),
    ]