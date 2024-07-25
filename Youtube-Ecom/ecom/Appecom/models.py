from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=150)

    def __str__(self):
        return self.name
    

class Profil(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=10)
    password = models.CharField(max_length=50)

    def __str__(self):
        return f'{self.user.first_name} - {self.user.last_name}'
    

class Product(models.Model):
    name = models.CharField(max_length=150)
    price = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    description = models.TextField()
    image = models.ImageField(upload_to="ProductImage")

    is_sale = models.BooleanField(default=False)
    sale_price = models.DecimalField(max_digits=7, decimal_places=2, default=0)


    def __str__(self):
        return self.name
    

class BasketProduct(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    prod_total_price = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return self.product.name

class Order(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    profil = models.ForeignKey(Profil, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    address = models.TextField()
    create_date = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(default=False)

    def __str__(self):
        return self.product.name