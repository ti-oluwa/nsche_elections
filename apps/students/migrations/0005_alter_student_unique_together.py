# Generated by Django 5.1.1 on 2024-09-19 00:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0004_alter_student_options_alter_student_unique_together'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='student',
            unique_together={('email', 'matriculation_number')},
        ),
    ]
