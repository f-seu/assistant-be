# Generated by Django 5.0.6 on 2024-06-20 17:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='messagemodel',
            old_name='sender',
            new_name='role',
        ),
    ]
