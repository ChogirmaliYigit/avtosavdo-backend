# Generated by Django 5.0.4 on 2024-04-30 11:14

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0006_alter_user_username"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="user",
            name="is_active",
        ),
        migrations.AddField(
            model_name="user",
            name="is_blocked",
            field=models.BooleanField(default=False),
        ),
        migrations.DeleteModel(
            name="BlockedUser",
        ),
    ]
