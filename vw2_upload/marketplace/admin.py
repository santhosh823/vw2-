from django.contrib import admin
from .models import (UserProfile, VehicleCategory, Seller, Vehicle,
                     SavedListing, Review, Enquiry,
                     Conversation, Message, VehicleBookingRequest)

@admin.register(UserProfile)
class UPAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'phone', 'location', 'is_verified']
    list_filter  = ['role', 'is_verified']

@admin.register(VehicleCategory)
class VCAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'icon']

@admin.register(Seller)
class SAdmin(admin.ModelAdmin):
    list_display  = ['name', 'phone', 'email', 'location', 'is_verified', 'rating']
    list_editable = ['is_verified']
    search_fields = ['name', 'email', 'location']

@admin.register(Vehicle)
class VAdmin(admin.ModelAdmin):
    list_display  = ['title', 'brand', 'model_name', 'category', 'price', 'year',
                     'status', 'is_featured', 'views_count']
    list_filter   = ['category', 'fuel_type', 'status', 'is_featured', 'condition']
    search_fields = ['title', 'brand', 'model_name']
    list_editable = ['status', 'is_featured']

@admin.register(Enquiry)
class EAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'vehicle', 'created_at']

@admin.register(Review)
class RAdmin(admin.ModelAdmin):
    list_display = ['user', 'seller', 'rating', 'created_at']

@admin.register(Conversation)
class ConvAdmin(admin.ModelAdmin):
    list_display = ['buyer', 'seller', 'vehicle', 'updated_at']

@admin.register(Message)
class MsgAdmin(admin.ModelAdmin):
    list_display = ['sender', 'conversation', 'is_read', 'sent_at']
    list_filter  = ['is_read']

@admin.register(VehicleBookingRequest)
class BRAdmin(admin.ModelAdmin):
    list_display  = ['buyer', 'vehicle', 'seller', 'status', 'created_at']
    list_filter   = ['status']
    list_editable = ['status']

admin.site.register(SavedListing)
