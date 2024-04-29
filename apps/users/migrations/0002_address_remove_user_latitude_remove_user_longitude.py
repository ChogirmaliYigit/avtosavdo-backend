# Generated by Django 5.0.4 on 2024-04-29 16:19

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Address",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("deleted_at", models.DateTimeField(blank=True, null=True)),
                ("address", models.TextField(blank=True, null=True)),
                ("latitude", models.FloatField()),
                ("longitude", models.FloatField()),
            ],
            options={
                "db_table": "addresses",
            },
        ),
        migrations.RemoveField(
            model_name="user",
            name="latitude",
        ),
        migrations.RemoveField(
            model_name="user",
            name="longitude",
        ),
    ]
