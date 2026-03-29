import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User
from marketplace.models import VehicleCategory, Seller, Vehicle, UserProfile

print("🌱 Seeding Vehicle World v2 (Upload Edition)...")

# Categories
cats = {}
for slug, name, icon, desc in [
    ('two_wheeler',   'Two Wheeler',   '🏍️', 'Motorcycles, scooters and electric bikes'),
    ('three_wheeler', 'Three Wheeler', '🛺', 'Auto rickshaws and cargo vehicles'),
    ('four_wheeler',  'Four Wheeler',  '🚗', 'Cars, SUVs and luxury vehicles'),
]:
    c, _ = VehicleCategory.objects.get_or_create(
        slug=slug, defaults={'name': name, 'icon': icon, 'description': desc})
    cats[slug] = c
    print(f"  ✅ Category: {name}")

# Admin
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@vw2.com', 'admin123')
    print("  ✅ admin / admin123")

# Sellers
sellers = []
seller_data = [
    ('ravi_motors',  'Ravi',     'Kumar',  'ravi@motors.in',  'seller123', '+91 98765 43210', 'Mumbai, Maharashtra',  'Premium two-wheeler dealer with 10+ years.'),
    ('priya_auto',   'Priya',    'Sharma', 'priya@auto.in',   'seller123', '+91 87654 32109', 'Bangalore, Karnataka', 'Luxury SUV & sedan specialist.'),
    ('kumar_wheels', 'Kumar',    'Raj',    'kumar@wheels.in', 'seller123', '+91 76543 21098', 'Chennai, Tamil Nadu',  'All categories. Best prices guaranteed.'),
    ('singh_motors', 'Gurpreet', 'Singh',  'singh@motors.in', 'seller123', '+91 65432 10987', 'Delhi, NCR',           'North India trusted dealer since 2010.'),
]
for uname, fn, ln, email, pwd, phone, loc, bio in seller_data:
    if not User.objects.filter(username=uname).exists():
        u = User.objects.create_user(uname, email, pwd, first_name=fn, last_name=ln)
        UserProfile.objects.create(user=u, role='seller', phone=phone, location=loc, bio=bio)
        s = Seller.objects.create(user=u, name=f"{fn} {ln}", phone=phone,
                                  email=email, location=loc, bio=bio)
        print(f"  ✅ Seller: {uname} / {pwd}")
    else:
        u = User.objects.get(username=uname)
        s, _ = Seller.objects.get_or_create(user=u, defaults={
            'name': f"{fn} {ln}", 'phone': phone, 'email': email,
            'location': loc, 'bio': bio})
    sellers.append(s)

# Buyer
if not User.objects.filter(username='buyer1').exists():
    bu = User.objects.create_user('buyer1', 'buyer@vw2.com', 'buyer123',
                                  first_name='Arjun', last_name='Mehta')
    UserProfile.objects.create(user=bu, role='buyer',
                               phone='+91 99999 00001', location='Hyderabad, Telangana')
    print("  ✅ Buyer: buyer1 / buyer123")

# Vehicles
vehicles = [
    dict(title='Royal Enfield Classic 350', category=cats['two_wheeler'], seller=sellers[0],
         brand='Royal Enfield', model_name='Classic 350', price=195000,
         fuel_type='petrol', year=2023, mileage='35 km/l', km_driven=5000,
         condition='excellent', color='Stealth Black', engine_cc='349cc',
         description='Iconic retro motorcycle. All original parts. Service done.', is_featured=True),
    dict(title='Honda Activa 6G — Like New', category=cats['two_wheeler'], seller=sellers[0],
         brand='Honda', model_name='Activa 6G', price=72000,
         fuel_type='petrol', year=2023, mileage='60 km/l', km_driven=2000,
         condition='excellent', color='Pearl White', engine_cc='109cc', is_featured=True),
    dict(title='Ola S1 Pro Electric Scooter', category=cats['two_wheeler'], seller=sellers[1],
         brand='Ola', model_name='S1 Pro', price=138000, original_price=155000,
         fuel_type='electric', year=2023, mileage='181 km/charge', km_driven=1500,
         condition='excellent', color='Midnight Blue', engine_cc='8.5kW Motor',
         description='Premium EV. Fast charging. Latest software.', is_featured=True),
    dict(title='TVS Apache RTR 200 4V', category=cats['two_wheeler'], seller=sellers[2],
         brand='TVS', model_name='Apache RTR 200', price=148000,
         fuel_type='petrol', year=2022, mileage='40 km/l', km_driven=12000,
         condition='good', color='Matte Red', engine_cc='197cc'),
    dict(title='Hero Splendor Plus', category=cats['two_wheeler'], seller=sellers[3],
         brand='Hero', model_name='Splendor Plus', price=68000,
         fuel_type='petrol', year=2022, mileage='70 km/l', km_driven=18000,
         condition='good', color='Black'),
    dict(title='Bajaj RE CNG Auto Rickshaw', category=cats['three_wheeler'], seller=sellers[2],
         brand='Bajaj', model_name='RE Compact', price=245000,
         fuel_type='cng', year=2022, mileage='35 km/kg', km_driven=45000,
         condition='good', description='All permits valid. Well maintained.', is_featured=True),
    dict(title='Mahindra Treo Electric Rickshaw', category=cats['three_wheeler'], seller=sellers[1],
         brand='Mahindra', model_name='Treo', price=315000, original_price=340000,
         fuel_type='electric', year=2023, mileage='130 km/charge', km_driven=8000,
         condition='excellent', description='Zero emission. Low running cost.'),
    dict(title='Piaggio Ape City Plus', category=cats['three_wheeler'], seller=sellers[3],
         brand='Piaggio', model_name='Ape City Plus', price=275000,
         fuel_type='petrol', year=2022, mileage='28 km/l', km_driven=22000, condition='good'),
    dict(title='Hyundai Creta SX+ Sunroof 2023', category=cats['four_wheeler'], seller=sellers[1],
         brand='Hyundai', model_name='Creta SX+', price=1850000, original_price=2050000,
         fuel_type='petrol', year=2023, mileage='17 km/l', km_driven=8000,
         condition='excellent', color='Atlas White', engine_cc='1497cc',
         description='Top variant. Panoramic sunroof.', is_featured=True),
    dict(title='Tata Nexon EV Max', category=cats['four_wheeler'], seller=sellers[3],
         brand='Tata', model_name='Nexon EV Max', price=1950000,
         fuel_type='electric', year=2023, mileage='437 km/charge', km_driven=5000,
         condition='excellent', color='Daytona Grey', engine_cc='40.5kWh',
         description="India's #1 electric SUV. 5-star NCAP.", is_featured=True),
    dict(title='Maruti Swift ZXi+', category=cats['four_wheeler'], seller=sellers[0],
         brand='Maruti Suzuki', model_name='Swift ZXi+', price=895000,
         fuel_type='petrol', year=2023, mileage='23 km/l', km_driven=3000,
         condition='excellent', color='Speedy Blue', engine_cc='1197cc'),
    dict(title='Toyota Innova Crysta GX', category=cats['four_wheeler'], seller=sellers[2],
         brand='Toyota', model_name='Innova Crysta', price=2050000,
         fuel_type='diesel', year=2022, mileage='15 km/l', km_driven=25000,
         condition='good', color='Silver', engine_cc='2755cc'),
    dict(title='Mahindra Thar LX 4x4', category=cats['four_wheeler'], seller=sellers[3],
         brand='Mahindra', model_name='Thar LX', price=1720000,
         fuel_type='diesel', year=2023, mileage='15 km/l', km_driven=6000,
         condition='excellent', color='Rocky Beige', engine_cc='2184cc',
         description='Adventure ready. Hardtop. Rock Terrain Tech.', is_featured=True),
    dict(title='Honda City ZX Hybrid', category=cats['four_wheeler'], seller=sellers[1],
         brand='Honda', model_name='City Hybrid', price=1590000,
         fuel_type='hybrid', year=2023, mileage='26 km/l', km_driven=4000,
         condition='excellent', color='Lunar Silver', engine_cc='1498cc'),
    dict(title='Kia Seltos HTX+ Diesel', category=cats['four_wheeler'], seller=sellers[0],
         brand='Kia', model_name='Seltos HTX+', price=1620000, original_price=1780000,
         fuel_type='diesel', year=2022, mileage='18 km/l', km_driven=15000,
         condition='good', color='Glacier White', engine_cc='1493cc'),
    dict(title='Bajaj Pulsar NS200', category=cats['two_wheeler'], seller=sellers[0],
         brand='Bajaj', model_name='Pulsar NS200', price=142000,
         fuel_type='petrol', year=2023, mileage='38 km/l', km_driven=4000,
         condition='excellent', color='Fiery Orange', engine_cc='199cc'),
]

for vd in vehicles:
    if not Vehicle.objects.filter(brand=vd['brand'], model_name=vd['model_name'], year=vd['year']).exists():
        Vehicle.objects.create(**vd)
        print(f"  ✅ {vd['brand']} {vd['model_name']}")

print()
print("=" * 55)
print("✅  SEED COMPLETE — Vehicle World v2 (Upload Edition)")
print("=" * 55)
print("  🌐 http://127.0.0.1:8000/")
print("  🛠️  /admin/         → admin / admin123")
print("  🏪 Seller: ravi_motors  / seller123")
print("  🏪 Seller: priya_auto   / seller123")
print("  🛒 Buyer:  buyer1       / buyer123")
print("=" * 55)
