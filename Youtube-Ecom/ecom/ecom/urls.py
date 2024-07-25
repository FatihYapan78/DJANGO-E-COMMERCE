from django.contrib import admin
from django.urls import path
from Appecom.views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", index, name="index"),
    path("product_detail/<int:product_id>/", product_detail, name="product_detail"),
    path("search/", search, name="search"),
    path("cart_summary/", cart_summary, name="cart_summary"),
    path("add_to_cart/", add_to_cart, name="add_to_cart"),
    path("update_to_cart/", update_to_cart, name="update_to_cart"),
    path("delete_to_cart/", delete_to_cart, name="delete_to_cart"),
    path("login", Login, name="login"),
    path("register", Register, name="register"),
    path("logout", Logout, name="logout"),
] + static(settings.MEDIA_URL, document_root =settings.MEDIA_ROOT)
