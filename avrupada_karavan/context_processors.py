from .forms import SubscriptionForm
from .models import FooterMenu, Brand, Product


def subscription_form(request):
    return {'subscription_form': SubscriptionForm()}


def footer_menu(request):
    products = Product.objects.all()[0:5]
    brands = Brand.objects.all()[0:5]
    footer_menus = FooterMenu.objects.all()[0:5]
    return {'footer_menus': footer_menus, 'products': products, 'brands': brands}
