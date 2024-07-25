from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpResponseRedirect
from .models import *
from .cart import Cart
from django.http.response import JsonResponse

def index(request):
    cart = Cart(request)
    products = Product.objects.all()
    return render(request, "index.html",{"products":products})


def search(request):

    if request.method == "POST":
        query = request.POST.get("query")

        products = Product.objects.filter(name__icontains=query)

        product_list = list(products.values("id", "name", "image"))

        for i in product_list:
            print(i)


        return JsonResponse({"product_list":product_list})


def product_detail(request, product_id):

    product = Product.objects.get(id=product_id)

    return render(request, "shop-detail.html", {"product":product})

def cart_summary(request):
    cart = Cart(request)
    products = cart.get_prods()
    prod_total_price = cart.prod_total_price()
    total_price = cart.total_price()
    quantities = request.session.get("cart")
    if request.user.is_authenticated:
        products = BasketProduct.objects.filter(user=request.user)
        

    return render(request, "cart.html",{"products":products,"quantities":quantities,"prod_total_price":prod_total_price,"total_price":total_price})

def add_to_cart(request):
    cart = Cart(request)

    if request.method == "POST":
        product_id = request.POST.get("product_id")
        qty = int(request.POST.get("qty", 1))
        print("qty",qty)
        product = Product.objects.get(id=product_id)

        cart.add(product=product,qty=qty)
        cart_quantity = cart.__len__()
        print(request.session["cart"])

        return JsonResponse({"cart_quantity":cart_quantity,"message":f"{product.name} sepete eklendi."})

def update_to_cart(request):
    cart = Cart(request)

    if request.method == "POST":
        product_id = request.POST.get("product_id")
        btn_qty = request.POST.get("btn_qty")
        product = Product.objects.get(id=product_id)
        cart.update(product=product,btn_qty=btn_qty, qty=1)
        if request.user.is_authenticated:
            prod_total_price = BasketProduct.objects.get(product=product).prod_total_price
        else:
            prod_total_price = cart.prod_total_price()
        total_price = cart.total_price()

    return JsonResponse({"product_total_price":prod_total_price,"total_price":total_price, "message":"Sepetiniz güncellendi."})
    

def delete_to_cart(request):
    cart = Cart(request)

    if request.method == "POST":
        product_id = request.POST.get("product_id")
        product = Product.objects.get(id=product_id)
        cart.delete(product=product)
        cart_quantity = cart.__len__()
        total_price = cart.total_price()

        return JsonResponse({"cart_quantity":cart_quantity, "total_price":total_price, "message":f"{product.name } sepetten kaldırıldı."})



def Login(request):
    cart = Cart(request)
    print(request.session.get("cart"))
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            if user.check_password(password):
                cart_products = request.session.get("cart")
                for product_id, value in cart_products.items():
                    product = Product.objects.get(id=product_id)
                    if BasketProduct.objects.filter(product=product).exists():
                        update_product = BasketProduct.objects.get(product=product)
                        update_product.quantity += value["qty"]
                        update_product.save()
                    else:
                        new_product = BasketProduct.objects.create(
                            user=user, product=product, quantity=value["qty"], prod_total_price=value["price"]
                        )
                        new_product.save()
                login(request, user)

                return redirect("index")
            else:
                messages.warning(request, "Parolanız Yanlış Lütfen Tekrar Deneyin")
        else:
            messages.warning(request, "E-Mail Adresiniz Yanlış Lütfen Tekrar Deneyin")
    
    return render(request, "login.html")

def Register(request):

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        if not User.objects.filter(email=email).exists():
            user = User.objects.create_user(username=email, email=email, password=password)
            user.save()
            login(request, user)
            return redirect("index")
        else:
            messages.warning(request, "E-Mail Adres Zaten Kullanılıyor. Lütfen Tekrar Deneyin")

    return render(request, "register.html")


def Logout(request):
    logout(request)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', 'index'))


