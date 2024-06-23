import django_filters
from django import forms
from .models import Product, Brand, Category


class ProductFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr='gte', label='Min Fiyat €')
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr='lte', label='Max Fiyat €')
    brand = django_filters.ModelChoiceFilter(queryset=Brand.objects.all(), label='Marka')
    category = django_filters.ModelChoiceFilter(queryset=Category.objects.all(), label='Kategori')
    mileage = django_filters.NumberFilter(label='Min KM', lookup_expr='gte')
    registration_year = django_filters.NumberFilter(field_name="registration_date", lookup_expr='year', label='Kayıt '
                                                                                                              'Yılı')
    power = django_filters.NumberFilter(label='Motor Gücü')
    fuel_type = django_filters.CharFilter(lookup_expr='icontains', label='Yakıt Tipi')
    transmission = django_filters.CharFilter(lookup_expr='icontains', label='Vites')
    color = django_filters.CharFilter(lookup_expr='icontains', label='Renk')
    title = django_filters.CharFilter(lookup_expr='icontains', label='İlan Başlığı')

    # Diğer alanlarınızı buraya ekleyebilirsiniz.

    def __init__(self, *args, **kwargs):
        super(ProductFilter, self).__init__(*args, **kwargs)

    class Meta:
        model = Product
        fields = ['brand', 'category', 'mileage', 'registration_year', 'power', 'fuel_type', 'transmission', 'color',
                  'min_price', 'max_price', 'title']
