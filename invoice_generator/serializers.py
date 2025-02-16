from rest_framework import serializers
from invoice_generator import models

class CustomerSerializer(serializers.ModelSerializer):

  class Meta:
    model = models.Customer
    fields = "__all__"

class ProductSerializer(serializers.ModelSerializer):

  class Meta:
    model = models.Product
    fields = "__all__"


class InvoiceSerializer(serializers.ModelSerializer):
  
  class Meta:
    model = models.InvoiceData
    fields = "__all__"


class ActivitySerializer(serializers.ModelSerializer):

  class Meta:
    model = models.RecentActivity
    fields = '__all__'