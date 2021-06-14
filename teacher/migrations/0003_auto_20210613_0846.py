# Generated by Django 3.2.4 on 2021-06-13 08:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teacher', '0002_teacher_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='teacher',
            name='subjects',
        ),
        migrations.AddField(
            model_name='teacher',
            name='subjects',
            field=models.JSONField(default=[]),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='Subject',
        ),
    ]