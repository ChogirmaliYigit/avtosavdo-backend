# Generated by Django 5.0.4 on 2024-04-30 07:08

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0005_user_username"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="username",
            field=models.CharField(default=1, max_length=1000, unique=True),
            preserve_default=False,
        ),
    ]
