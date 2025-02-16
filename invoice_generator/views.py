from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db.models import Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import login as auth_login, authenticate, logout
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view
from django.core.serializers import serialize
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework import status
from django.core.files.base import ContentFile
from num2words import num2words
from .serializers import *
from .models import *
from datetime import *
import base64
import json
import os


# Create your views here.
@login_required
def home(request):
    user_data = User.objects.get(username=request.user)
    today = date.today()
    current_year = today.year
    start_date = date(
        current_year if today >= date(current_year, 4, 1) else current_year - 1, 4, 1
    )
    end_date = date(
        current_year + 1 if today >= date(current_year, 4, 1) else current_year, 3, 31
    )
    total_sales = InvoiceData.objects.filter(
        InvoiceDate__range=(start_date, end_date)
    ).aggregate(total=Sum("InvoiceTotal"))
    total_sales_amount = total_sales["total"]
    last_invoice = (
        InvoiceData.objects.filter(InvoiceDate__range=(start_date, end_date))
        .order_by("InvoiceNumber")
        .last()
    )
    total_products = len(Product.objects.all())
    activity = RecentActivity.objects.order_by("Date")[:3]
    paid_amount = (
        InvoiceData.objects.filter(InvoiceDate__range=(start_date, end_date))
        .filter(InvoiceStatus="Paid")
        .aggregate(total=Sum("InvoiceTotal"))
    )
    unpaid_amount = (
        InvoiceData.objects.filter(InvoiceDate__range=(start_date, end_date))
        .filter(InvoiceStatus="Unpaid")
        .aggregate(total=Sum("InvoiceTotal"))
    )
    print(paid_amount, unpaid_amount)
    context = {
        "user_data": user_data,
        "total_sales_amount": total_sales_amount,
        "last_invoice": last_invoice.InvoiceNumber,
        "total_products": total_products,
        "activity": activity,
        "paid_amount": paid_amount["total"],
        "unpaid_amount": unpaid_amount["total"],
    }
    return render(request, "index.html", context=context)


def user_login(request):
    if request.method == "POST":
        email = request.POST["Email"]
        password = request.POST["Password"]

        print(email, password)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return JsonResponse({"error": "No User Found"}, status=404)

        user = authenticate(username=user.username, password=password)

        if user is not None:
            auth_login(request, user)
            return redirect("/")
        else:
            return JsonResponse({"error": "Invalid Credentials"}, status=401)

    return render(request, "login.html")


def user_logout(request):
    logout(request)
    return redirect("/login/")


@login_required
def invoice(request):

    invoices = InvoiceData.objects.all()
    month = datetime.now().strftime("%b")
    paginator = Paginator(invoices, 10)
    print(month)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "invoices": serialize("json", invoices),
        "page_obj": page_obj,
        "month": month,
    }
    return render(request, "orders.html", context=context)


@login_required
@csrf_exempt
def paid(request, id):
    invoice = get_object_or_404(InvoiceData, id=id)
    invoice.InvoiceStatus = "Paid"
    invoice.save()

    return redirect("/invoice/")


@login_required
def GenerateInvoice(request):

    if request.method == "POST":
        customer = request.POST["customer"]
        products = request.POST["products"]

        request.session["customer"] = customer
        request.session["products"] = products

        return redirect("/invoice/bill/")

    return render(request, "invoice.html")


@login_required
def InvoiceHandler(request):
    date = datetime.now()

    customer_data = json.loads(request.session["customer"])[
        0
    ]  # Assuming it's a list with one customer object
    products_data = json.loads(request.session["products"])
    request.session["InvoiceNumber"] = get_next_bill_number()
    tax = tax_calc(request, products_data)
    context = {
        "InvoiceNumber": request.session["InvoiceNumber"],
        "customer": customer_data,
        "Products": products_data,
        "Date": date.strftime("%x"),
        "cgst": tax["cgst"],
        "sgst": tax["sgst"],
        "total": tax["total"],
        "grand_total": tax["grand_total"],
        "amt_in_words": tax["amt_in_words"],
    }

    return render(request, "invoice_template.html", context=context)


def get_next_bill_number():
    today = date.today()
    current_year = today.year
    start_date = date(
        current_year if today >= date(current_year, 4, 1) else current_year - 1, 4, 1
    )
    end_date = date(
        current_year + 1 if today >= date(current_year, 4, 1) else current_year, 3, 31
    )

    # Get the highest bill number for the current financial year
    last_invoice = (
        InvoiceData.objects.filter(InvoiceDate__range=(start_date, end_date))
        .order_by("InvoiceNumber")
        .last()
    )
    if last_invoice:
        return last_invoice.InvoiceNumber + 1
    else:
        return 1


def tax_calc(request, data):

    request.session["total"] = sum(data["total"] for data in data)

    request.session["grand_total"] = request.session["total"] + (
        0.18 * request.session["total"]
    )
    request.session["amt_in_words"] = num2words(
        request.session["grand_total"], lang="en_IN"
    )
    request.session["gst"] = 0.09 * request.session["total"]

    tax = {
        "total": request.session["total"],
        "sgst": request.session["gst"],
        "cgst": request.session["gst"],
        "grand_total": request.session["grand_total"],
        "amt_in_words": request.session["amt_in_words"],
    }

    return tax


@login_required
def save_invoice(request):
    if request.method == "POST":
        customer_data = json.loads(request.session["customer"])[0]

        # Ensure customer_data has the required field {Name}
        if "Name" not in customer_data:
            return redirect("/")

        customer_name = customer_data["Name"]

        try:
            data = {
                "InvoiceNumber": request.session["InvoiceNumber"],
                "CustomerName": customer_name,
                "InvoiceDate": datetime.now().date(),
                "InvoiceDescription": json.loads(request.session["products"]),
                "InvoiceTotal": request.session["grand_total"],
            }

            serializer = InvoiceSerializer(data=data)

            if serializer.is_valid():
                serializer.save()
                activity_data = {
                    "InvoiceNumber": request.session["InvoiceNumber"],
                    "Action": "Created",
                }
                activity_serializer = ActivitySerializer(data=activity_data)
                if activity_serializer.is_valid():
                    activity_serializer.save()
                    return redirect("/invoice/")
            else:
                print(serializer.errors)

        except Exception as e:
            print(f"Error saving invoice: {e}")

    return redirect("/")


@login_required
def customers(request):
    return render(request, "customers.html")


@login_required
def customer_profile(request, id):
    return render(request, "profile.html", context={"id": id})


@login_required
def Add_Customer(request):
    return render(request, "Add_Customer.html")


@login_required
def Edit_Customer(request, id):

    data = Customer.objects.get(id=id)

    context = {"data": data}

    return render(request, "Edit_Customer.html", context=context)


@login_required
def products(request):

    product_data = Product.objects.all()

    context = {"product_data": product_data}

    return render(request, "products.html", context=context)


@login_required
def Add_Products(request):

    if request.method == "POST":
        data = request.POST
        print(data)

        serializer = ProductSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return redirect("/products/")
        else:
            return JsonResponse(serializer.errors)

    return render(request, "Add_Products.html")


@login_required
def Edit_Product(request, id):

    data = Product.objects.get(id=id)

    context = {"data": data}

    if request.method == "POST":
        new_data = request.POST
        instance = get_object_or_404(Product, id=id)
        serializer = ProductSerializer(instance, data=new_data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return redirect("/products/")

    return render(request, "Edit_Product.html", context=context)


## API Views


@api_view(["GET"])
def Get_Customers(request):
    try:
        data = Customer.objects.all()
        if not data.exists():
            return Response({"message": "No Data Found! Insert Some."}, status=404)
        serializer = CustomerSerializer(data, many=True)
        return Response(serializer.data, status=200)
    except Exception as e:
        return Response({"error": str(e)}, status=500)


@api_view(["GET"])
def fetch_customer(request, name):
    data = Customer.objects.filter(Name__icontains=name)
    serializer = CustomerSerializer(data, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def fetch_product(request, name):
    data = Product.objects.filter(ProductName__icontains=name)
    serializer = ProductSerializer(data, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def fetch_invoice(request, id):
    today = date.today()
    current_year = today.year
    start_date = date(
        current_year if today >= date(current_year, 4, 1) else current_year - 1, 4, 1
    )
    end_date = date(
        current_year + 1 if today >= date(current_year, 4, 1) else current_year, 3, 31
    )

    date_info = {"start_date": start_date, "end_date": end_date}

    try:
        custdata = Customer.objects.get(id=id)
    except Customer.DoesNotExist:
        return Response("Error: Customer Does Not Exist", status=404)

    cust_serializer = CustomerSerializer(custdata)
    invdata = InvoiceData.objects.filter(CustomerName=custdata.Name)

    paginator = Paginator(invdata, 5)  # Show 5 invoices per page.
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)
    inv_serializer = InvoiceSerializer(page_obj, many=True)

    return JsonResponse(
        {
            "custdata": cust_serializer.data,
            "invdata": inv_serializer.data,
            "date_info": date_info,
            "page_info": {
                "current_page": page_obj.number,
                "num_pages": paginator.num_pages,
                "has_next": page_obj.has_next(),
                "has_previous": page_obj.has_previous(),
            },
        }
    )


@api_view(["POST"])
def Customer_API(request, id):

    if id > 0:
        try:
            customer = get_object_or_404(Customer, id=id)

            serializer = CustomerSerializer(
                customer, data=request.data, partial=True
            )  # Use partial=True to allow partial updates
            if serializer.is_valid():
                serializer.save()
                return redirect("/customers/")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except customer.DoesNotExist:
            data = request.POST

            serializer = CustomerSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return redirect("/customers/")
    elif id == 0:
        data = request.POST

        serializer = CustomerSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return redirect("/customers/")
