from .models import *
from decimal import Decimal


class Cart():
    def __init__(self, request):
        self.session = request.session
        self.user = request.user

        # Eğer mevcut bir oturum varsa o oturum içindeki cartı alıyoruz.
        cart = self.session.get("cart")

        # Eğer mevcut bir oturum yoksa yeni cart oluşturuyoruz.
        if cart is None:
            cart = self.session["cart"] = {}

        self.cart = cart

    def add(self, product,qty):
        product_id = str(product.id)

        if self.user.is_authenticated:
            if BasketProduct.objects.filter(product=product).exists():
                update_product = BasketProduct.objects.get(product=product)
                update_product.quantity += qty
                update_product.save()
            else:
                new_product = BasketProduct.objects.create(user=self.user, product=product,quantity=qty)
                new_product.save()
        else:
            if product_id in self.cart:
                self.cart[product_id]["qty"] += qty
            else:
                self.cart[product_id] = {"price": str(product.price), "qty":qty}
        
        # Sepeti güncellediğimiz için oturumu da güncellememiz gerekiyor.
        self.session.modified = True

    def update(self, product, btn_qty, qty):
        product_id = str(product.id)


        if self.user.is_authenticated:
            if btn_qty == "btn-plus":
                update_product = BasketProduct.objects.get(product=product)
                update_product.quantity += qty
                update_product.prod_total_price = Decimal(update_product.product.price) * Decimal(update_product.quantity)
                update_product.save()
            else:
                update_product = BasketProduct.objects.get(product=product)
                update_product.quantity -= qty
                update_product.prod_total_price = Decimal(update_product.product.price) * Decimal(update_product.quantity)
                update_product.save()
        else:
            if btn_qty == "btn-plus":
                self.cart[product_id]["qty"] += qty
                self.cart[product_id]["price"] = str(self.cart[product_id]["qty"] * product.price)
            else:
                self.cart[product_id]["qty"] -= qty
                self.cart[product_id]["price"] = str(self.cart[product_id]["qty"] * product.price)

        self.session.modified = True

    def delete(self, product):
        product_id = str(product.id)

        if self.user.is_authenticated:
            basket_product = BasketProduct.objects.get(product=product)
            basket_product.delete()
        else:
            if product_id in self.cart:
                del self.cart[product_id]

        self.session.modified = True

    def prod_total_price(self):
        for key, value in self.cart.items():
            self.cart[key]["price"] = str(Decimal(value["price"]) * Decimal(value["qty"]))

        return self.cart
    
    def total_price(self):
        total = Decimal('0.00')

        if self.user.is_authenticated:
            products = BasketProduct.objects.filter(user=self.user)
            for product in products:
                total += product.product.price * product.quantity
        else:
            for key, value in self.cart.items():
                total += Decimal(value["price"])

        return total

    def get_prods(self):
        product_ids = self.cart.keys()

        products = Product.objects.filter(id__in = product_ids)

        return products
    
    def __len__(self):
        if self.user.is_authenticated:
            products = BasketProduct.objects.filter(user=self.user)
            return len(products)
        else:
            return len(self.cart)