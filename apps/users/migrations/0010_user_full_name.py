# Generated by Django 5.0.4 on 2024-05-04 11:51

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0009_alter_address_options_alter_user_options_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="full_name",
            field=models.CharField(
                blank=True, max_length=200, null=True, verbose_name="Тўлиқ исми"
            ),
        ),
    ]
