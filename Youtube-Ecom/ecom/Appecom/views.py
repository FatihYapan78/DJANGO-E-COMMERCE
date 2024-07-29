from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpResponseRedirect
from .models import *
from .cart import Cart
from django.http.response import JsonResponse
import iyzipay
from decimal import Decimal
import json
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

def chackout(request):
    cart = Cart(request)
    profil = Profil.objects.get(user=request.user)
    basket_products = BasketProduct.objects.filter(user=request.user)
    total_price = cart.total_price()
    if request.method == "POST":
        options = {
        'api_key': 'sandbox-aWZXnJH7mZE6FCnRbDvvMUGbOkhDFSGG',
        'secret_key': 'sandbox-8ycQYYCXH46MCkz2xGtWSdDR0rx4bOI1',
        'base_url': 'sandbox-api.iyzipay.com'
        }

        name = request.POST.get("name")
        surname = request.POST.get("surname")
        adres = request.POST.get("adres")
        il = request.POST.get("il")
        ülke = request.POST.get("ülke")
        zip = request.POST.get("zip")
        tel = request.POST.get("tel")
        email = request.POST.get("email")
        cardNumber = request.POST.get("number")
        expiry = request.POST.get("expiry")
        cvc = request.POST.get("cvc")


        payment_card = {
            'cardHolderName': name +" "+ surname, # Kart sahibinin adı.
            'cardNumber': cardNumber, #  Kart numarası.
            'expireMonth': expiry.split("/")[0].strip(), # Kartın son kullanma ayı.
            'expireYear': expiry.split("/")[1].strip(), # Kartın son kullanma yılı.
            'cvc': cvc, # Kartın güvenlik kodu.
            'registerCard': '0' # Kartı kaydedip kaydetmeme durumu. '0' kaydetmez, '1' kaydeder.
        }

        buyer = {
            'id': request.user.id, # Alıcının ID'si.
            'name': name, #  Alıcının adı.
            'surname': surname, # Alıcının soyadı.
            'gsmNumber': tel, # Alıcının telefon numarası.
            'email': email, # Alıcının e-posta adresi.
            'identityNumber': '74300864791', # Alıcının kimlik numarası.
            'lastLoginDate': '2015-10-05 12:43:35', #  Alıcının en son giriş yaptığı tarih.
            'registrationDate': '2013-04-21 15:12:09', # Alıcının kayıt olduğu tarih.
            'registrationAddress': adres, # Alıcının kayıtlı adresi.
            'ip': request.META.get('REMOTE_ADDR'), # Alıcının IP adresi.
            'city': il, # Alıcının yaşadığı şehir.
            'country': ülke, # Alıcının yaşadığı ülke.
            'zipCode': zip # Alıcının posta kodu.
        }

        address = {
            'contactName': name +" "+ surname, # Adresle ilgili kişinin adı.
            'city': il, # Şehir.
            'country': ülke, # Ülke
            'address': adres, # Adres detayları.
            'zipCode': zip # Posta kodu.
        }

        basket_items = [
        ]
        prod_total_pric = 0
        for product in basket_products:
            prod_total_pric += float(product.prod_total_price)
            basket_item ={
                "id": product.product.id,
                "name": product.product.name,
                "category1": product.product.category.name,
                "itemType": 'PHYSICAL',
                "price": float(product.prod_total_price)
            }
            basket_items.append(basket_item)

        payment_request = {
            'locale': 'tr', # Dil ve yerel ayar 
            'conversationId': '123456789', # İsteğin konuşma ID'si  (genellikle benzersiz bir işlem numarası).
            'price': prod_total_pric, # Toplam tutar (vergiler hariç).
            'paidPrice': prod_total_pric, # Ödenen toplam tutar (vergiler dahil).
            'currency': 'TRY', # Para birimi ('TRY' Türk Lirası için).
            'installment': '1', # Taksit sayısı.
            'basketId': "1", # Sepet ID'si.
            'paymentChannel': 'WEB', #  Ödeme kanalı ('WEB' internet üzerinden ödeme için).
            'paymentGroup': 'PRODUCT', # Ödeme grubu ('PRODUCT' ürün ödemesi için).
            'paymentCard': payment_card, # Ödeme kartı bilgileri.
            'buyer': buyer, # Alıcı bilgileri.
            'shippingAddress': address, # Teslimat adresi.
            'billingAddress': address, # Fatura adresi.
            'basketItems': basket_items # Sepet öğeleri.
        }
        payment = iyzipay.Payment().create(payment_request, options)
        payment_result = json.loads(payment.read().decode('utf-8'))
        print(payment_result)
        if payment_result["status"] == "success":
            order = Order.objects.create(profil=profil, prod_total_price=total_price)
            for product in basket_products:
                order_item = OrderItems.objects.create(product = product.product, quantity=product.quantity, prod_total_price=product.prod_total_price)
                order_item.save()
                order.order_items.add(order_item)
                order.save()
        else:
            return redirect("chackout")

    context={
        "profil":profil,
        "basket_products":basket_products,
        "total_price":total_price
    }

    return render(request, "chackout.html", context)

    

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


