# Generated by Django 5.0.4 on 2024-04-30 07:03

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0004_remove_user_username"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="username",
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
    ]
