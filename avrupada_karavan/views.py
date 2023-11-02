from django.shortcuts import render


# Create your views here.

def main_page(request):
    return render(request, "main_page.html")
def search_result_page(request):
    return render(request, "search_result.html")
def car_detail_page(request):
    return render(request, "car_detail_page.html")
def login(request):
    return render(request, "login.html")
def register(request):
    return render(request, "register.html")


