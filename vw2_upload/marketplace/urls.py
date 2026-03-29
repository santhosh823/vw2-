from django.urls import path
from . import views

urlpatterns = [
    # ── Public ──────────────────────────────────────────────────────
    path('',                         views.home,             name='home'),
    path('listings/',                views.listings,         name='listings'),
    path('listings/<int:pk>/',       views.vehicle_detail,   name='vehicle_detail'),
    path('categories/<slug:slug>/',  views.category_view,    name='category'),
    path('sellers/',                 views.sellers_page,     name='sellers'),
    path('sellers/<int:pk>/',        views.seller_profile,   name='seller_profile'),
    path('electric/',                views.electric_hub,     name='electric_hub'),

    # ── Auth ────────────────────────────────────────────────────────
    path('register/',          views.register_choice,  name='register'),
    path('register/buyer/',    views.register_buyer,   name='register_buyer'),
    path('register/seller/',   views.register_seller,  name='register_seller'),
    path('login/',             views.login_view,        name='login'),
    path('logout/',            views.logout_view,       name='logout'),

    # ── Buyer ────────────────────────────────────────────────────────
    path('save/<int:pk>/',     views.toggle_save,       name='toggle_save'),
    path('saved/',             views.saved_listings,    name='saved'),

    # ── Booking Requests ─────────────────────────────────────────────
    path('book-request/<int:pk>/',              views.send_booking_request,   name='send_booking_request'),
    path('book-request/update/<int:req_id>/',   views.update_booking_request, name='update_booking_request'),

    # ── Chat ─────────────────────────────────────────────────────────
    path('chat/start/<int:vehicle_pk>/',    views.start_conversation,  name='start_conversation'),
    path('chat/',                           views.inbox,               name='inbox'),
    path('chat/<int:conv_id>/',             views.chat_detail,         name='chat_detail'),
    path('chat/<int:conv_id>/api/',         views.chat_messages_api,   name='chat_messages_api'),

    # ── Seller Dashboard ─────────────────────────────────────────────
    path('dashboard/',                      views.dashboard,           name='dashboard'),
    path('dashboard/add/',                  views.add_listing,         name='add_listing'),
    path('dashboard/edit/<int:pk>/',        views.edit_listing,        name='edit_listing'),
    path('dashboard/delete/<int:pk>/',      views.delete_listing,      name='delete_listing'),
    path('dashboard/sold/<int:pk>/',        views.mark_sold,           name='mark_sold'),
    path('dashboard/profile/',              views.seller_edit_profile, name='seller_edit_profile'),
]
