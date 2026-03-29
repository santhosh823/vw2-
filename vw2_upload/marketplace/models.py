from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


class UserProfile(models.Model):
    ROLE_CHOICES = [('buyer', 'Buyer'), ('seller', 'Seller')]
    user       = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role       = models.CharField(max_length=10, choices=ROLE_CHOICES, default='buyer')
    phone      = models.CharField(max_length=20, blank=True)
    location   = models.CharField(max_length=200, blank=True)
    bio        = models.TextField(blank=True)
    avatar     = models.ImageField(upload_to='avatars/', blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_seller(self): return self.role == 'seller'
    def is_buyer(self):  return self.role == 'buyer'
    def __str__(self):   return f"{self.user.username} ({self.role})"


class VehicleCategory(models.Model):
    SLUG_CHOICES = [
        ('two_wheeler',   'Two Wheeler'),
        ('three_wheeler', 'Three Wheeler'),
        ('four_wheeler',  'Four Wheeler'),
    ]
    name        = models.CharField(max_length=100)
    slug        = models.CharField(max_length=50, choices=SLUG_CHOICES, unique=True)
    description = models.TextField(blank=True)
    icon        = models.CharField(max_length=10, default='🚗')
    cover_color = models.CharField(max_length=20, default='#FF4500')

    class Meta: verbose_name_plural = 'Vehicle Categories'
    def __str__(self): return self.name


class Seller(models.Model):
    user       = models.OneToOneField(User, on_delete=models.CASCADE,
                                      related_name='seller_profile', null=True, blank=True)
    name       = models.CharField(max_length=150)
    phone      = models.CharField(max_length=20)
    email      = models.EmailField()
    location   = models.CharField(max_length=200)
    avatar     = models.ImageField(upload_to='sellers/', blank=True, null=True)
    bio        = models.TextField(blank=True)
    is_verified = models.BooleanField(default=False)
    rating     = models.DecimalField(max_digits=3, decimal_places=1, default=4.5)
    total_sales = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):       return self.name
    def listing_count(self): return self.listings.filter(status='active').count()


class Vehicle(models.Model):
    FUEL_CHOICES = [
        ('petrol', 'Petrol'), ('diesel', 'Diesel'),
        ('electric', 'Electric'), ('hybrid', 'Hybrid'), ('cng', 'CNG'),
    ]
    STATUS_CHOICES    = [('active', 'Active'), ('sold', 'Sold'), ('inactive', 'Inactive')]
    CONDITION_CHOICES = [
        ('new', 'Brand New'), ('excellent', 'Excellent'),
        ('good', 'Good'), ('fair', 'Fair'),
    ]

    title          = models.CharField(max_length=200)
    category       = models.ForeignKey(VehicleCategory, on_delete=models.CASCADE, related_name='listings')
    seller         = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name='listings')
    brand          = models.CharField(max_length=100)
    model_name     = models.CharField(max_length=100)
    price          = models.DecimalField(max_digits=12, decimal_places=2)
    original_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    fuel_type      = models.CharField(max_length=20, choices=FUEL_CHOICES)
    year           = models.IntegerField()
    mileage        = models.CharField(max_length=50)
    km_driven      = models.PositiveIntegerField(default=0, help_text='KM driven (0 for brand new)')
    condition      = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='good')
    color          = models.CharField(max_length=50, blank=True)
    engine_cc      = models.CharField(max_length=30, blank=True, help_text='e.g. 110cc or 1497cc')
    description    = models.TextField(blank=True)
    image          = models.ImageField(upload_to='vehicles/', blank=True, null=True)
    image2         = models.ImageField(upload_to='vehicles/', blank=True, null=True)
    image3         = models.ImageField(upload_to='vehicles/', blank=True, null=True)
    status         = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    is_featured    = models.BooleanField(default=False)
    is_negotiable  = models.BooleanField(default=True)
    views_count    = models.PositiveIntegerField(default=0)
    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)

    class Meta: ordering = ['-created_at']

    def __str__(self): return f"{self.brand} {self.model_name} ({self.year})"

    def formatted_price(self):
        p = float(self.price)
        if p >= 10000000: return f'₹{p/10000000:.2f} Cr'
        elif p >= 100000: return f'₹{p/100000:.2f} L'
        return f'₹{p:,.0f}'

    def discount_pct(self):
        if self.original_price and self.original_price > self.price:
            return int(((self.original_price - self.price) / self.original_price) * 100)
        return 0

    def is_new_listing(self):
        return (timezone.now() - self.created_at) < timedelta(days=7)


class SavedListing(models.Model):
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved')
    vehicle    = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='saved_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta: unique_together = ('user', 'vehicle')
    def __str__(self): return f"{self.user.username} saved {self.vehicle.title}"


class Review(models.Model):
    seller     = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name='reviews')
    user       = models.ForeignKey(User, on_delete=models.CASCADE)
    rating     = models.PositiveSmallIntegerField(default=5)
    comment    = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta: unique_together = ('seller', 'user')
    def __str__(self): return f"{self.user.username} → {self.seller.name}: {self.rating}★"


class Enquiry(models.Model):
    vehicle    = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='enquiries')
    name       = models.CharField(max_length=100)
    email      = models.EmailField()
    phone      = models.CharField(max_length=20)
    message    = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self): return f"Enquiry: {self.name} → {self.vehicle.title}"


class Conversation(models.Model):
    vehicle    = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='conversations')
    buyer      = models.ForeignKey(User, on_delete=models.CASCADE, related_name='buyer_conversations')
    seller     = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name='seller_conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('vehicle', 'buyer', 'seller')
        ordering = ['-updated_at']

    def __str__(self): return f"{self.buyer.username} ↔ {self.seller.name}"

    def last_message(self):        return self.messages.last()
    def unread_for_seller(self):   return self.messages.filter(sender=self.buyer, is_read=False).count()
    def unread_for_buyer(self):    return self.messages.filter(is_read=False).exclude(sender=self.buyer).count()


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    body         = models.TextField()
    is_read      = models.BooleanField(default=False)
    sent_at      = models.DateTimeField(auto_now_add=True)

    class Meta: ordering = ['sent_at']
    def __str__(self): return f"{self.sender.username}: {self.body[:40]}"


class VehicleBookingRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'), ('accepted', 'Accepted'),
        ('rejected', 'Rejected'), ('completed', 'Completed'),
    ]
    vehicle    = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='booking_requests')
    buyer      = models.ForeignKey(User, on_delete=models.CASCADE, related_name='booking_requests')
    seller     = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name='booking_requests')
    status     = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    message    = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self): return f"{self.buyer.username} → {self.vehicle.title} [{self.status}]"
