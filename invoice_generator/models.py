from django.db import models

# Create your models here.
class Customer(models.Model):
  Name = models.CharField(max_length=100)
  Address = models.CharField(max_length=1000)
  PhoneNumber = models.BigIntegerField()
  EMail = models.EmailField()
  GstNumber = models.CharField(max_length=20)
  PlaceOfSupply = models.CharField(max_length=30)


class Product(models.Model):
  ProductName = models.CharField(max_length=30)
  ProductHSNCode = models.CharField(max_length=30)


class InvoiceData(models.Model):
  InvoiceNumber = models.IntegerField()
  CustomerName = models.CharField(max_length=100)
  InvoiceDate = models.DateField()
  InvoiceDescription = models.JSONField(default=dict)
  InvoiceTotal = models.IntegerField()
  InvoiceStatus = models.CharField(max_length=25, default="Unpaid")
  PaymentMethod = models.CharField(max_length=50, null=True)
  CreatedAt = models.DateTimeField(auto_now=True)

  def __str__(self):
    return f"Invoice {self.pk} - {self.CustomerName}"


class RecentActivity(models.Model):
  InvoiceNumber = models.IntegerField()
  Action = models.CharField(max_length=1000)
  Date = models.DateField(auto_now=True)
  Time = models.TimeField(auto_now=True)
