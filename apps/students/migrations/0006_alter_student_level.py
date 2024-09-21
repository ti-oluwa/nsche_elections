# Generated by Django 5.1.1 on 2024-09-21 13:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0005_alter_student_unique_together'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='level',
            field=models.CharField(choices=[('100', '100 Level'), ('200', '200 Level'), ('300', '300 Level'), ('400', '400 Level'), ('500', '500 Level'), ('600', '600 Level'), ('700', '700 Level')], max_length=120),
        ),
    ]
