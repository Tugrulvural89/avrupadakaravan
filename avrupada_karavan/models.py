from django.contrib.auth.models import User
from django.db import models
from ckeditor.fields import RichTextField
from django.template.defaultfilters import slugify

# Create your models here.
"""
from django.db import models
from ckeditor.fields import RichTextField

class Product(models.Model):
    # ...
    description = RichTextField()
    # ...
"""


class HomePageImageModel(models.Model):
    desktop_image = models.ImageField(upload_to='images/desktop')
    mobile_image = models.ImageField(upload_to='images/mobile')
    alt_text = models.CharField(max_length=255)
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "Home Page Images"
        verbose_name = "Home Page Image"
        ordering = ['title']


class BlogPage(models.Model):
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='images/blog')
    alt_text = models.CharField(max_length=255)
    description = RichTextField()
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    published = models.BooleanField(default=False)
    slug = models.SlugField(max_length=200, unique=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(BlogPage, self).save(*args, **kwargs)

    def __str__(self):
        return self.title


class SingleImagePage(models.Model):
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='images/single')
    alt_text = models.CharField(max_length=255)

    def __str__(self):
        return self.title


# Category model
class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


# Brand model
class Brand(models.Model):
    name = models.CharField(max_length=100)
    founded_year = models.IntegerField()
    image = models.ImageField(upload_to='brand_images/', blank=True, null=True)

    def __str__(self):
        return self.name


# Product model
class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)  # ForeignKey relationship to Category
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True)  # ForeignKey relationship to Brand
    mileage = models.IntegerField(help_text='in kilometers')
    transmission = models.CharField(max_length=100)
    registration_date = models.DateField()
    power = models.CharField(max_length=50, help_text='in kW (horsepower)')
    fuel_type = models.CharField(max_length=50)
    number_of_owners = models.IntegerField(default=1)
    permissible_gross_weight = models.IntegerField(help_text='in kilograms')
    HU = models.DateField(blank=True, null=True)  # General inspection date
    air_conditioning = models.CharField(max_length=100, blank=True)
    color = models.CharField(max_length=50, blank=True)
    axles = models.IntegerField(default=2)
    number_of_sleeping_places = models.IntegerField(default=2)
    title = models.CharField(max_length=250, default='Production')
    description = models.TextField(default='Production')
    price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    url = models.CharField(max_length=300, blank=True, null=True)

    def __str__(self):
        return f"{self.id}"

    @property
    def formatted_price(self):
        if self.price is not None:
            # Format the price as 1.000.000,00 TL
            formatted_price = "{:,.2f}".format(self.price).replace(",", "X").replace(".", ",").replace("X", ".")
            return f"{formatted_price} TL"
        return "N/A"
    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"


class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)

    def __str__(self):
        return str(self.pk)


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user.username} - {self.product.title}"


class ContactForm(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name}"


class Subscription(models.Model):
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.email}"


class StaticPage(models.Model):
    title = models.CharField(max_length=255)
    url = models.URLField(max_length=255)
    image = models.ImageField(upload_to='static_page_images/', blank=True, null=True)
    alt_text = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title}"


class FooterMenu(models.Model):
    title = models.CharField(max_length=255)
    static_page = models.ManyToManyField(StaticPage)

    def __str__(self):
        return f"{self.title}"


class ContactPageInfo(models.Model):
    title = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    tel = models.CharField(max_length=255)
    whatsapp = models.CharField(max_length=255)
    facebook_url = models.CharField(max_length=255)
    instagram_url = models.CharField(max_length=255)
    twitter_url = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.title}"
