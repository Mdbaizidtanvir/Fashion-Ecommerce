from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone  # Add this import

class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    main_image = models.ImageField(upload_to='products/', blank=True, null=True)
    size = models.CharField(max_length=100)
    color = models.CharField(max_length=100)
    category = models.CharField(max_length=90)  # fixed spelling from "catagory"

    def __str__(self):
        return self.name

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/extra/')

    def __str__(self):
        return f"Image for {self.product.name}"


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
            ('cancelled', 'Cancelled'),  # ✅ new

    ]

    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    products = models.ManyToManyField(Product, through='OrderItem')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default='pending')
    payment_staus = models.CharField(max_length=300, choices=PAYMENT_STATUS_CHOICES, default='pending')
    email = models.EmailField()
    phone = models.CharField(max_length=100)
    address = models.TextField()
    zip_code = models.CharField(max_length=20)
    delivery_date = models.DateField(null=True, blank=True)
    card_last4 = models.CharField(max_length=4, blank=True, null=True)
    paid_at = models.DateTimeField(null=True, blank=True)  # ✅ new field to track when payment was made
    stripe_payment_intent = models.CharField(max_length=255, null=True, blank=True)  # ✅ Add this line

    def __str__(self):
        return f"Order #{self.id} for {self.email}"

    def save(self, *args, **kwargs):
        if not self.delivery_date:
            self.delivery_date = timezone.now().date() + timedelta(days=3)
        super().save(*args, **kwargs)

        # Update total price from related OrderItems
        total = sum(
            item.price * item.quantity for item in self.orderitem_set.all()
        )
        if self.total_price != total:
            self.total_price = total
            super().save(update_fields=['total_price'])

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='favorited_by')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')  # Prevent duplicate favorites

    def __str__(self):
        return f"{self.user.username} likes {self.product.name}"

class ReturnRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE)
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    pickup_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"ReturnRequest - {self.user.username} - {self.order_item.product.name}"


class NewsletterEmail(models.Model):
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
