# Generated by Django 5.1.1 on 2024-09-19 22:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_useraccount_timezone'),
    ]

    operations = [
        migrations.AlterField(
            model_name='useraccount',
            name='is_admin',
            field=models.BooleanField(default=False),
        ),
    ]
