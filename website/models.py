# website/models.py

from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField

class Category(models.Model):
    name = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=200, unique=True)
    class Meta:
        ordering = ('name',)
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name

# Model for Products
class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=200, db_index=True)
    image = CloudinaryField('image', blank=True, null=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    available = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('name',)
        # This is the new, correct way to create a multi-column index
        indexes = [
            models.Index(fields=['id', 'slug']),
        ]
    def __str__(self):
        return self.name

# Model for Orders
class Order(models.Model):
    STATUS_CHOICES = [
        ('processing', 'Processing'),       # Order paid, awaiting fulfillment
        ('shipped', 'Shipped'),           # Order fulfilled and sent
        ('delivered', 'Delivered'),       # Order received by customer
        ('cancelled', 'Cancelled'),       # Order cancelled
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='processing')
    stripe_id = models.CharField(max_length=255, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    address = models.CharField(max_length=250)
    postal_code = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    paid = models.BooleanField(default=False)

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return f'Order {self.id}'

# Model for items within an Order
class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return str(self.id)

    def get_cost(self):
        return self.price * self.quantity

class Collection(models.Model):
    GENDER_CHOICES = [
        ('her', 'For Her'),
        ('him', 'For Him'),
        ('them', 'For Them'),
    ]
    gender_category = models.CharField(max_length=4, choices=GENDER_CHOICES, default='them')

    name = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='collections/%Y/%m/%d', blank=True)
    products = models.ManyToManyField(Product, related_name='collections', blank=True)
    is_active = models.BooleanField(default=True) # So you can hide/show collections

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name