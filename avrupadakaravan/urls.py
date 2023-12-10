"""
URL configuration for avrupadakaravan project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from avrupada_karavan import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = ([
    path("admin/", admin.site.urls),
    path("", views.main_page, name="main_page"),
    path("search/", views.search_result_page, name="search_result_page"),
    path("detail/<int:product_id>", views.car_detail_page, name="car_detail_page"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register, name="register"),
    path("blog/", views.blog_main, name="blog_main"),
    path("blog/<slug:slug>", views.blog_detail, name="blog_detail"),
    path("contact/", views.contact, name="contact"),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('nasil-calisir/', views.how_works, name="howworks"),
    path('favorite/<int:product_id>/', views.toggle_favorites, name='toggle_favorite'),
    path('favoriler/', views.user_favorites, name="user_favorites"),
    path('subscribe/', views.subscribe, name="subscribe"),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
               + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT))
