# Generated by Django 5.1.1 on 2024-09-19 23:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('elections', '0004_election_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='election',
            name='slug',
            field=models.SlugField(default='wertfyuijokplbnm', editable=False, help_text='Unique identifier for the election. Used in URLs.', unique=True),
        ),
    ]
