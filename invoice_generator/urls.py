from django.urls import path
from .views import *

urlpatterns = [
  path('', home, name="home"),
  path('login/', user_login, name="login"),
  path('logout/', user_logout, name="user_logout"),
  path('customers/', customers, name="customers"),
  path('customers/<id>/profile', customer_profile, name="customer_profile"),
  path('add-customer/', Add_Customer, name="Add_Customer"),
  path('edit-customer/<id>', Edit_Customer, name="Edit_Customer"),
  path('invoice/', invoice, name="invoice"),
  path('paid/<id>', paid, name="paid"),
  path('generate-invoice/', GenerateInvoice, name="GenerateInvoice"),
  path('invoice/bill/', InvoiceHandler, name="InvoiceHandler"),
  path('save-invoice/', save_invoice, name="save_invoice"),
  path('products/', products, name="products"),
  path('add-product/', Add_Products, name="Add_Products"),
  path('edit-product/<id>/', Edit_Product, name="Edit_Product"),
  #api urls
  path('api/customers/', Get_Customers, name="Get_Customers"),
  path('api/customer/<name>', fetch_customer, name="fetch_customer"),
  path('api/customer/<int:id>/', Customer_API, name="Customer_API"),
  path('api/product/<name>', fetch_product, name="fetch_product"),
  path('api/invoice/<int:id>', fetch_invoice, name="fetch_invoice")
]