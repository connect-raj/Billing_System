from django.shortcuts import render
from rest_framework.response import Response as res
from invoice_generator.models import *
import json
from django.core.serializers import serialize

# Create your views here.
def index(request):

  queryset = serialize('json', InvoiceData.objects.all(), fields=('InvoiceDescription'))

  return render(request, "stockindex.html", context= {"queryset":queryset})