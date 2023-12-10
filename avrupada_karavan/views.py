import time
from datetime import datetime

from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect

from .forms import LoginForm, RegisterForm, SubscriptionForm
from .models import HomePageImageModel, BlogPage, SingleImagePage, Product, Favorite, Brand, ContactPageInfo
from django.core.paginator import Paginator

from .filters import ProductFilter
from .forms import ContactForm
from .models import ContactForm as ContactFormModel

import requests
from bs4 import BeautifulSoup

from django.contrib.admin.views.decorators import staff_member_required


# Create your views here.
def main_page(request):
    images = HomePageImageModel.objects.all()
    user_agent = request.META['HTTP_USER_AGENT']
    contents = BlogPage.objects.all()
    blog_main_image = SingleImagePage.objects.filter(title='main_blog').first()
    product_filters = ProductFilter(request.GET, queryset=Product.objects.all())
    all_brands = Brand.objects.all()[0:6]
    products = Product.objects.all()[0:4]
    return render(request, "main_page.html", {'products': products, 'images': images, 'isMobile': user_agent,
                                              'contents': contents, 'blog_main_image': blog_main_image,
                                              'product_filters': product_filters, 'all_brands': all_brands})


def search_result_page(request):
    product_filters = ProductFilter(request.GET, queryset=Product.objects.all())
    return render(request, "search_result.html", {
        'product_filters': product_filters})


def car_detail_page(request, product_id):
    product = Product.objects.get(id=product_id)
    favorites_count = Favorite.objects.filter(user=request.user, product=product).count()

    return render(request, "car_detail_page.html", {'product': product, 'favorites_count': favorites_count})


def login_view(request):
    if request.method == 'POST':
        print(request.POST.dict())
        form = LoginForm(request.POST or None)
        if form.is_valid():
            print('asdasd')
            cd = form.cleaned_data
            username = cd['username']
            password = cd['password']
            print(username, password)
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('main_page')
    else:
        form = LoginForm()
    return render(request, "login.html", {'form': form})


def logout_view(request):
    logout(request)
    return render(request, "login.html")


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # Kullanıcı kayıt olduktan sonra giriş sayfasına yönlendir
    else:
        form = RegisterForm()
        return render(request, "register.html", {'form': form})


def contact(request):
    contact_form = ContactPageInfo.objects.all().first()
    if request.method == 'POST':
        if request.COOKIES.get('form_sent'):
            return HttpResponse("Teşekkürler, formunuz zaten gönderilmiş.")
        form = ContactForm(request.POST)
        if form.is_valid():
            ContactFormModel.objects.create(**form.cleaned_data)
            response = HttpResponse('Formunuz Alındı.')
            response.set_cookie('form_sent', 'true', max_age=86400)
            return response
    else:
        form = ContactForm()
    return render(request, "contact_page.html", {'form': form,
                                                 'contact_form': contact_form })


def how_works(request):
    return render(request, "how_works.html", {})


def blog_main(request):
    all_posts = BlogPage.objects.all()
    paginator = Paginator(all_posts, 2)  # Her sayfada 10 gönderi göster
    page_number = request.GET.get('page')
    contents = paginator.get_page(page_number)

    return render(request, "blog_main_page.html", {'contents': contents})


def blog_detail(request, slug=None):
    # this is blog detail page get_or_404 method
    blog = get_object_or_404(BlogPage, slug=slug)
    return render(request, "blog_detail_page.html", {'post': blog})


def toggle_favorites(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    favorite, created = Favorite.objects.get_or_create(user=request.user, product=product)
    if not created:
        favorite.delete()
    return redirect('car_detail_page', product_id=product_id)


def user_favorites(request):
    favorites = Favorite.objects.filter(user=request.user)
    return render(request, 'favorite_items.html', {'favorites': favorites})


def subscribe(request):
    if request.COOKIES.get('form_sent'):
        return HttpResponse("Teşekkürler, formunuz zaten gönderilmiş.")
    if request.method == 'POST':
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            form.save()
            response = HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
            response.set_cookie('form_sent', 'true', max_age=86400)
            return response

