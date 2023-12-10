from django.contrib import admin
from .models import HomePageImageModel, BlogPage, SingleImagePage, Category, Brand, Product, ProductImage, Subscription, \
    ContactPageInfo
from .models import FooterMenu, StaticPage


# Register your models here.


class FooterMenuAdmin(admin.ModelAdmin):
    fields = ['static_page', 'title']


admin.site.register(FooterMenu, FooterMenuAdmin)


class StaticPageAdmin(admin.ModelAdmin):
    list_display = ('title', 'url', 'image', 'alt_text', 'description', 'created_at', 'updated_at', 'published')


admin.site.register(StaticPage, StaticPageAdmin)


class HomePageImageModelAmin(admin.ModelAdmin):
    list_display = ('title', 'alt_text', 'desktop_image', 'mobile_image')


admin.site.register(HomePageImageModel, HomePageImageModelAmin)


class BlogPageAdmin(admin.ModelAdmin):
    list_display = ('title', 'image', 'alt_text', 'description', 'create_at', 'update_at', 'published')


admin.site.register(BlogPage, BlogPageAdmin)


class SingleImagePageAdmin(admin.ModelAdmin):
    list_display = ('title', 'image', 'alt_text')


admin.site.register(SingleImagePage, SingleImagePageAdmin)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')


admin.site.register(Category, CategoryAdmin)


class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'founded_year')


admin.site.register(Brand, BrandAdmin)


class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'category', 'brand', 'mileage', 'transmission', 'registration_date', 'power', 'fuel_type', 'number_of_owners',
        'permissible_gross_weight', 'HU', 'air_conditioning', 'color', 'axles', 'number_of_sleeping_places')


admin.site.register(Product, ProductAdmin)


class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'image')


admin.site.register(ProductImage, ProductImageAdmin)


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('email', 'created_at')


admin.site.register(Subscription, SubscriptionAdmin)


class ContactPageInfoAdmin(admin.ModelAdmin):
    fields = ['title', 'facebook_url', 'email', 'tel', 'twitter_url', 'instagram_url', 'whatsapp']


admin.site.register(ContactPageInfo, ContactPageInfoAdmin)
