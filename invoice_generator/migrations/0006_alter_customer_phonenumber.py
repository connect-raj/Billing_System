# Generated by Django 5.0.6 on 2024-07-13 11:38

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("invoice_generator", "0005_invoicedata_invoicenumber"),
    ]

    operations = [
        migrations.AlterField(
            model_name="customer",
            name="PhoneNumber",
            field=models.BigIntegerField(),
        ),
    ]
