# Generated by Django 5.0.4 on 2024-04-30 06:34

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0003_address_user"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="user",
            name="username",
        ),
    ]
