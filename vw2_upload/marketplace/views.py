from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Sum
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
import json

from .models import (Vehicle, VehicleCategory, Seller, SavedListing,
                     UserProfile, Review, Enquiry,
                     Conversation, Message, VehicleBookingRequest)
from .forms import (BuyerRegisterForm, SellerRegisterForm, LoginForm,
                    AddVehicleForm, EditVehicleForm, EnquiryForm,
                    SearchForm, SellerProfileForm)


# ── helpers ──────────────────────────────────────────────────────────────────

def _role(user):
    try:    return user.profile.role
    except: return None


def seller_required(fn):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please login to continue.')
            return redirect('login')
        if _role(request.user) != 'seller':
            messages.error(request, 'This page is for seller accounts only.')
            return redirect('home')
        return fn(request, *args, **kwargs)
    wrapper.__name__ = fn.__name__
    return wrapper


# ══ PUBLIC VIEWS ══════════════════════════════════════════════════════════════

def home(request):
    categories  = VehicleCategory.objects.all()
    featured    = Vehicle.objects.filter(status='active', is_featured=True)[:6]
    latest      = Vehicle.objects.filter(status='active').order_by('-created_at')[:8]
    electric    = Vehicle.objects.filter(status='active', fuel_type='electric')[:4]
    top_sellers = Seller.objects.annotate(cnt=Count('listings')).order_by('-cnt')[:4]
    two_w       = Vehicle.objects.filter(status='active', category__slug='two_wheeler').order_by('-created_at')[:8]
    three_w     = Vehicle.objects.filter(status='active', category__slug='three_wheeler').order_by('-created_at')[:8]
    four_w      = Vehicle.objects.filter(status='active', category__slug='four_wheeler').order_by('-created_at')[:8]
    stats = {
        'vehicles': Vehicle.objects.filter(status='active').count(),
        'sellers':  Seller.objects.count(),
        'brands':   Vehicle.objects.values('brand').distinct().count(),
        'cities':   Seller.objects.values('location').distinct().count(),
    }
    return render(request, 'marketplace/home.html', {
        'categories': categories, 'featured': featured, 'latest': latest,
        'electric': electric, 'top_sellers': top_sellers, 'stats': stats,
        'two_w': two_w, 'three_w': three_w, 'four_w': four_w,
    })


def listings(request):
    qs = Vehicle.objects.filter(status='active').select_related('category', 'seller')
    form = SearchForm(request.GET)
    categories = VehicleCategory.objects.all()

    q         = request.GET.get('q', '').strip()
    category  = request.GET.get('category', '')
    fuel      = request.GET.get('fuel', '')
    min_p     = request.GET.get('min_price', '')
    max_p     = request.GET.get('max_price', '')
    sort      = request.GET.get('sort', '')
    condition = request.GET.get('condition', '')

    if q:        qs = qs.filter(Q(brand__icontains=q) | Q(model_name__icontains=q) | Q(title__icontains=q))
    if category: qs = qs.filter(category__slug=category)
    if fuel:     qs = qs.filter(fuel_type=fuel)
    if min_p:    qs = qs.filter(price__gte=min_p)
    if max_p:    qs = qs.filter(price__lte=max_p)
    if condition: qs = qs.filter(condition=condition)

    if sort == 'price_asc':   qs = qs.order_by('price')
    elif sort == 'price_desc': qs = qs.order_by('-price')
    elif sort == 'year_desc':  qs = qs.order_by('-year')
    else:                      qs = qs.order_by('-created_at')

    return render(request, 'marketplace/listings.html', {
        'vehicles': qs, 'form': form, 'categories': categories,
        'total': qs.count(), 'q': q, 'selected_cat': category,
    })


def vehicle_detail(request, pk):
    v = get_object_or_404(Vehicle, pk=pk, status='active')
    v.views_count += 1
    v.save(update_fields=['views_count'])

    related = Vehicle.objects.filter(category=v.category, status='active').exclude(pk=pk)[:4]
    is_saved = (request.user.is_authenticated and
                SavedListing.objects.filter(user=request.user, vehicle=v).exists())
    existing_request = None
    if request.user.is_authenticated and _role(request.user) == 'buyer':
        existing_request = VehicleBookingRequest.objects.filter(
            vehicle=v, buyer=request.user).first()

    form = EnquiryForm()
    if request.method == 'POST':
        form = EnquiryForm(request.POST)
        if form.is_valid():
            e = form.save(commit=False)
            e.vehicle = v
            e.save()
            messages.success(request, f'✅ Enquiry sent to {v.seller.name}!')
            return redirect('vehicle_detail', pk=pk)

    return render(request, 'marketplace/vehicle_detail.html', {
        'v': v, 'related': related, 'is_saved': is_saved,
        'form': form, 'existing_request': existing_request,
    })


def category_view(request, slug):
    cat = get_object_or_404(VehicleCategory, slug=slug)
    vehicles = Vehicle.objects.filter(category=cat, status='active')
    fuel = request.GET.get('fuel', '')
    sort = request.GET.get('sort', '')
    if fuel: vehicles = vehicles.filter(fuel_type=fuel)
    if sort == 'price_asc':   vehicles = vehicles.order_by('price')
    elif sort == 'price_desc': vehicles = vehicles.order_by('-price')
    all_cats = VehicleCategory.objects.all()
    return render(request, 'marketplace/category.html', {
        'cat': cat, 'vehicles': vehicles, 'all_cats': all_cats,
        'fuel': fuel, 'sort': sort,
    })


def sellers_page(request):
    sellers = Seller.objects.annotate(cnt=Count('listings')).order_by('-cnt')
    return render(request, 'marketplace/sellers.html', {'sellers': sellers})


def seller_profile(request, pk):
    seller   = get_object_or_404(Seller, pk=pk)
    vehicles = Vehicle.objects.filter(seller=seller, status='active')
    reviews  = Review.objects.filter(seller=seller).order_by('-created_at')
    return render(request, 'marketplace/seller_profile.html', {
        'seller': seller, 'vehicles': vehicles, 'reviews': reviews,
    })


def electric_hub(request):
    vehicles = Vehicle.objects.filter(status='active', fuel_type='electric').order_by('-created_at')
    return render(request, 'marketplace/electric_hub.html', {'vehicles': vehicles})


# ══ AUTH ══════════════════════════════════════════════════════════════════════

def register_choice(request):
    if request.user.is_authenticated:
        return redirect('home')
    return render(request, 'marketplace/register_choice.html')


def register_buyer(request):
    if request.user.is_authenticated:
        return redirect('home')
    form = BuyerRegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        UserProfile.objects.create(
            user=user, role='buyer',
            phone=form.cleaned_data.get('phone', ''),
        )
        login(request, user)
        messages.success(request, f'Welcome, {user.first_name}! Start exploring vehicles.')
        return redirect('home')
    return render(request, 'marketplace/register_buyer.html', {'form': form})


def register_seller(request):
    if request.user.is_authenticated:
        return redirect('home')
    form = SellerRegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        UserProfile.objects.create(
            user=user, role='seller',
            phone=form.cleaned_data.get('phone', ''),
            location=form.cleaned_data.get('location', ''),
            bio=form.cleaned_data.get('bio', ''),
        )
        Seller.objects.create(
            user=user,
            name=f"{user.first_name} {user.last_name}".strip() or user.username,
            phone=form.cleaned_data.get('phone', ''),
            email=user.email,
            location=form.cleaned_data.get('location', ''),
            bio=form.cleaned_data.get('bio', ''),
        )
        login(request, user)
        messages.success(request, 'Seller account created! Add your first vehicle now.')
        return redirect('dashboard')
    return render(request, 'marketplace/register_seller.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    form = LoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = authenticate(
            request,
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password'],
        )
        if user:
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            return redirect('dashboard' if _role(user) == 'seller' else 'home')
        messages.error(request, 'Invalid username or password.')
    return render(request, 'marketplace/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('home')


# ══ BUYER VIEWS ══════════════════════════════════════════════════════════════

@login_required
def toggle_save(request, pk):
    v = get_object_or_404(Vehicle, pk=pk)
    obj, created = SavedListing.objects.get_or_create(user=request.user, vehicle=v)
    if not created:
        obj.delete()
        messages.info(request, 'Removed from saved.')
    else:
        messages.success(request, 'Saved! ❤️')
    return redirect(request.META.get('HTTP_REFERER', 'home'))


@login_required
def saved_listings(request):
    saved = SavedListing.objects.filter(user=request.user).select_related('vehicle')
    return render(request, 'marketplace/saved.html', {'saved': saved})


# ══ BOOKING REQUEST ═══════════════════════════════════════════════════════════

@login_required
def send_booking_request(request, pk):
    v = get_object_or_404(Vehicle, pk=pk, status='active')
    if _role(request.user) != 'buyer':
        messages.error(request, 'Only buyers can send booking requests.')
        return redirect('vehicle_detail', pk=pk)
    msg = request.POST.get('message', '')
    VehicleBookingRequest.objects.get_or_create(
        vehicle=v, buyer=request.user, seller=v.seller,
        defaults={'message': msg},
    )
    messages.success(request, f'Booking request sent to {v.seller.name}!')
    return redirect('vehicle_detail', pk=pk)


@seller_required
def update_booking_request(request, req_id):
    seller = get_object_or_404(Seller, user=request.user)
    br = get_object_or_404(VehicleBookingRequest, pk=req_id, seller=seller)
    new_status = request.POST.get('status')
    if new_status in ['accepted', 'rejected', 'completed']:
        br.status = new_status
        br.save()
        messages.success(request, f'Request marked as {new_status}.')
    return redirect('dashboard')


# ══ CHAT ══════════════════════════════════════════════════════════════════════

@login_required
def start_conversation(request, vehicle_pk):
    v = get_object_or_404(Vehicle, pk=vehicle_pk, status='active')
    if _role(request.user) == 'seller':
        messages.error(request, 'Sellers cannot start chats.')
        return redirect('vehicle_detail', pk=vehicle_pk)
    conv, _ = Conversation.objects.get_or_create(
        vehicle=v, buyer=request.user, seller=v.seller)
    return redirect('chat_detail', conv_id=conv.pk)


@login_required
def inbox(request):
    user = request.user
    role = _role(user)
    if role == 'seller':
        seller = get_object_or_404(Seller, user=user)
        convs  = Conversation.objects.filter(seller=seller).select_related(
            'vehicle', 'buyer').order_by('-updated_at')
        unread_total = sum(c.unread_for_seller() for c in convs)
    else:
        convs  = Conversation.objects.filter(buyer=user).select_related(
            'vehicle', 'seller').order_by('-updated_at')
        unread_total = sum(c.unread_for_buyer() for c in convs)
    return render(request, 'marketplace/inbox.html', {
        'convs': convs, 'role': role, 'unread_total': unread_total,
    })


@login_required
def chat_detail(request, conv_id):
    user = request.user
    role = _role(user)
    conv = get_object_or_404(Conversation, pk=conv_id)

    if role == 'seller':
        seller = get_object_or_404(Seller, user=user)
        if conv.seller != seller:
            messages.error(request, 'Access denied.')
            return redirect('inbox')
        conv.messages.filter(is_read=False).exclude(sender=user).update(is_read=True)
    else:
        if conv.buyer != user:
            messages.error(request, 'Access denied.')
            return redirect('inbox')
        conv.messages.filter(is_read=False).exclude(sender=user).update(is_read=True)

    if request.method == 'POST':
        body = request.POST.get('body', '').strip()
        if body:
            Message.objects.create(conversation=conv, sender=user, body=body)
            conv.updated_at = timezone.now()
            conv.save(update_fields=['updated_at'])
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'ok'})
        return redirect('chat_detail', conv_id=conv_id)

    msgs = conv.messages.select_related('sender').all()
    return render(request, 'marketplace/chat_detail.html', {
        'conv': conv, 'msgs': msgs, 'role': role,
    })


@login_required
def chat_messages_api(request, conv_id):
    conv  = get_object_or_404(Conversation, pk=conv_id)
    after = request.GET.get('after', 0)
    msgs  = conv.messages.filter(pk__gt=after).values(
        'id', 'body', 'sent_at', 'sender__username', 'is_read')
    data  = [{**m, 'sent_at': m['sent_at'].isoformat()} for m in msgs]
    return JsonResponse({'messages': data})


# ══ SELLER DASHBOARD ══════════════════════════════════════════════════════════

@seller_required
def dashboard(request):
    seller      = get_object_or_404(Seller, user=request.user)
    my_vehicles = Vehicle.objects.filter(seller=seller).order_by('-created_at')
    booking_requests = VehicleBookingRequest.objects.filter(
        seller=seller).select_related('buyer', 'vehicle').order_by('-created_at')

    # Chart: listings added per month (last 6 months)
    now = timezone.now()
    chart_labels, chart_data = [], []
    for i in range(5, -1, -1):
        dt = now - timedelta(days=30 * i)
        chart_labels.append(dt.strftime('%b %Y'))
        chart_data.append(
            my_vehicles.filter(created_at__year=dt.year,
                               created_at__month=dt.month).count())

    # Chart: top viewed vehicles
    top_views    = my_vehicles.filter(views_count__gt=0).order_by('-views_count')[:6]
    views_labels = [f"{v.brand} {v.model_name}" for v in top_views]
    views_data   = [v.views_count for v in top_views]

    convs       = Conversation.objects.filter(seller=seller)
    unread_msgs = sum(c.unread_for_seller() for c in convs)

    stats = {
        'total':       my_vehicles.count(),
        'active':      my_vehicles.filter(status='active').count(),
        'sold':        my_vehicles.filter(status='sold').count(),
        'featured':    my_vehicles.filter(is_featured=True).count(),
        'views':       my_vehicles.aggregate(t=Sum('views_count'))['t'] or 0,
        'enquiries':   Enquiry.objects.filter(vehicle__seller=seller).count(),
        'pending_req': booking_requests.filter(status='pending').count(),
        'unread_msgs': unread_msgs,
    }
    recent_enquiries = Enquiry.objects.filter(
        vehicle__seller=seller).order_by('-created_at')[:5]

    return render(request, 'marketplace/dashboard.html', {
        'seller':           seller,
        'vehicles':         my_vehicles,
        'stats':            stats,
        'enquiries':        recent_enquiries,
        'booking_requests': booking_requests[:10],
        'chart_labels':     json.dumps(chart_labels),
        'chart_data':       json.dumps(chart_data),
        'views_labels':     json.dumps(views_labels),
        'views_data':       json.dumps(views_data),
    })


@seller_required
def add_listing(request):
    """
    Add a new vehicle listing — handles image upload via request.FILES.
    The form MUST use enctype='multipart/form-data' (set in template).
    """
    seller = get_object_or_404(Seller, user=request.user)

    if request.method == 'POST':
        # Pass both request.POST (text data) AND request.FILES (uploaded images)
        form = AddVehicleForm(request.POST, request.FILES)
        if form.is_valid():
            vehicle         = form.save(commit=False)
            vehicle.seller  = seller
            vehicle.save()
            messages.success(request, f'✅ "{vehicle.title}" listed successfully!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = AddVehicleForm()

    return render(request, 'marketplace/add_listing.html', {'form': form})


@seller_required
def edit_listing(request, pk):
    """
    Edit an existing listing — images optional, won't clear existing if not re-uploaded.
    """
    seller  = get_object_or_404(Seller, user=request.user)
    vehicle = get_object_or_404(Vehicle, pk=pk, seller=seller)

    if request.method == 'POST':
        form = EditVehicleForm(request.POST, request.FILES, instance=vehicle)
        if form.is_valid():
            form.save()
            messages.success(request, f'"{vehicle.title}" updated successfully!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = EditVehicleForm(instance=vehicle)

    return render(request, 'marketplace/edit_listing.html', {'form': form, 'v': vehicle})


@seller_required
def delete_listing(request, pk):
    seller  = get_object_or_404(Seller, user=request.user)
    vehicle = get_object_or_404(Vehicle, pk=pk, seller=seller)
    if request.method == 'POST':
        name = vehicle.title
        vehicle.delete()
        messages.success(request, f'"{name}" deleted.')
        return redirect('dashboard')
    return render(request, 'marketplace/confirm_delete.html', {'v': vehicle})


@seller_required
def mark_sold(request, pk):
    seller  = get_object_or_404(Seller, user=request.user)
    vehicle = get_object_or_404(Vehicle, pk=pk, seller=seller)
    vehicle.status = 'sold'
    vehicle.save()
    messages.success(request, f'"{vehicle.title}" marked as sold.')
    return redirect('dashboard')


@seller_required
def seller_edit_profile(request):
    """
    Seller can update their name, contact info, bio, and profile avatar photo.
    """
    seller  = get_object_or_404(Seller, user=request.user)
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = SellerProfileForm(request.POST, request.FILES)
        if form.is_valid():
            seller.name     = form.cleaned_data['name']
            seller.phone    = form.cleaned_data['phone']
            seller.location = form.cleaned_data['location']
            seller.bio      = form.cleaned_data.get('bio', '')
            if form.cleaned_data.get('avatar'):
                seller.avatar = form.cleaned_data['avatar']
            seller.save()

            request.user.email = form.cleaned_data['email']
            request.user.save()

            messages.success(request, 'Profile updated successfully!')
            return redirect('seller_edit_profile')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = SellerProfileForm(initial={
            'name':     seller.name,
            'phone':    seller.phone,
            'email':    request.user.email,
            'location': seller.location,
            'bio':      seller.bio,
        })

    return render(request, 'marketplace/seller_edit_profile.html', {
        'form': form, 'seller': seller,
    })
