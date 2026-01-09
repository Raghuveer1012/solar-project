from django.shortcuts import render


def home_view(request):
    return render(request, "home.html")


def about_view(request):
    return render(request, "about.html")


def contact_view(request):
    return render(request, "contact.html")


def products_view(request):
    return render(request, "products.html")


def solar_calculator(request):
    return render(request, "solar_calculator.html")
