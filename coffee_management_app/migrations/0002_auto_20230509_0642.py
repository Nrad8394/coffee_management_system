# Generated by Django 3.0.7 on 2023-05-09 03:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('coffee_management_app', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='adminmanager',
            old_name='admin',
            new_name='user',
        ),
    ]
