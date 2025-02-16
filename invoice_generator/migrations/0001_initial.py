# Generated by Django 5.0.6 on 2024-06-28 18:44

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Customer",
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
                ("Name", models.CharField(max_length=30)),
                ("Address", models.CharField(max_length=1000)),
                ("PhoneNumber", models.IntegerField()),
                ("EMail", models.EmailField(max_length=254)),
                ("GstNumber", models.CharField(max_length=20)),
                ("PlaceOfSupply", models.CharField(max_length=30)),
            ],
        ),
    ]
