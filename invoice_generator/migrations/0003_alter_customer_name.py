# Generated by Django 5.0.6 on 2024-07-04 14:16

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("invoice_generator", "0002_product"),
    ]

    operations = [
        migrations.AlterField(
            model_name="customer",
            name="Name",
            field=models.CharField(max_length=100),
        ),
    ]
