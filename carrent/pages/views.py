from django.shortcuts import render, redirect
from django.contrib import messages
from django.shortcuts import get_object_or_404
from .models import ContactMessage
from django.utils.dateparse import parse_date
from django.db.models import Q
from datetime import datetime
from .models import Car, Reservation, Client
from django.core.exceptions import ValidationError

def home(request):
    return render(request, 'index.html')

def cars(request):
    return render(request, 'cars.html')

def contact(request):
    client_id = request.session.get('client_id')
    context = {}

    if client_id:
        client = Client.objects.get(id=client_id)
        context['name'] = client.name
        context['email'] = client.email

    # ✅ ارسال فرم
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        if not all([name, email, message]):
            context['error'] = 'Please fill all fields'
            return render(request, 'contact.html', context)

        ContactMessage.objects.create(name=name, email=email, message=message)
        context['success'] = 'Message sent successfully'
        return render(request, 'contact.html', context)

    return render(request, 'contact.html', context)

def login(request):
    return render(request, 'login.html')

def logout(request):
    request.session.flush()   # ✅ پاک کردن کامل session
    return redirect('home')

def reserve(request):
    # ✅ 1. check login
    client_id = request.session.get('client_id')
    if not client_id:
        return redirect('login')

    # ✅ 2. get logged-in user
    customer = Client.objects.get(id=client_id)

    # ✅ 3. get only user's reservations
    reservations = Reservation.objects.filter(
        customer=customer
    ).select_related('car').order_by('-created_at')

    return render(request, 'my-reservation.html', {
        'reservations': reservations
    })

def register(request):
    return render(request, 'register.html')

def success(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)
    return render(request, 'success.html', {'reservation': reservation})

def booking(request):
    if not request.session.get('client_id'):
        return redirect('login')
    # فقط خودروهایی که status آنها 'available' است را می‌فرستیم
    available_cars = Car.objects.filter(status='available')
    context = {
        'cars': available_cars
    }
    return render(request, 'booking.html', context)

def confirm(request):
    client_id = request.session.get('client_id')
    if not client_id:
        return redirect('login')
    if request.method != "POST":
        return redirect("booking")

    car_id = request.POST.get("car_id")
    start_date = request.POST.get("start_date")
    end_date = request.POST.get("end_date")

    if not all([car_id, start_date, end_date]):
        messages.error(request, "Please fill all fields")
        return redirect("booking")

    start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

    car = Car.objects.get(id=car_id)

    conflict = Reservation.objects.filter(
        car=car,
        status__in=["pending", "confirmed"]
    ).filter(
        Q(start_date__lte=end_date) & Q(end_date__gte=start_date)
    )

    if conflict.exists():
        messages.error(request, "Selected car is not available")
        return redirect("booking")

    customer = Client.objects.get(id=client_id)
    try:
            reservation = Reservation.objects.create(
            customer=customer,
            car=car,
            start_date=start_date,
            end_date=end_date,
            status="pending"
            )
    except ValidationError as e:
            messages.error(request, "End date cannot be before start date")
            return redirect("booking")


    car.status = "rented"
    car.save()

    messages.success(request, "Reservation created successfully!")
    return redirect("success", reservation_id=reservation.id)

def register_submit(request):
    """پردازش فرم ثبت‌نام"""
    if request.method == 'POST':
        # 🔴 دریافت داده‌ها
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        context = {}  # برای ارسال خطا به template
        
        # 🔴 ۱. بررسی پر بودن همه فیلدها
        if not all([name, email, phone, password, confirm_password]):
            context['error'] = 'Please fill all fields'
            return render(request, 'register.html', context)
        
        # 🔴 ۲. بررسی مطابقت پسوردها
        if password != confirm_password:
            context['error'] = 'Passwords do not match'
            return render(request, 'register.html', context)
        
        # 🔴 ۳. بررسی وجود کاربر با این ایمیل
        if Client.objects.filter(email=email).exists():
            context['error'] = 'Email already registered'
            return render(request, 'register.html', context)
        
        
        
        try:
            
            # 🔴 ۵. ایجاد کاربر جدید
            client = Client.objects.create(
                name=name,
                email=email,
                phone=phone,
                password=password
            )
            
            print(f"✅ user created: {client.id}")
            
            # 🔴 ۶. انتقال مستقیم به صفحه لاگین
            return redirect('login')
            
        except Exception as e:
            print(f"❌ error: {e}")
            context['error'] = f'Registration failed: {str(e)}'
            return render(request, 'register.html', context)
    
    # اگر GET request
    return redirect('register')

def login_submit(request):
    """Process login form"""
    if request.method == 'POST':
        # 🔴 get email & password from form
        email = request.POST.get('email')
        password = request.POST.get('password')

        print(f"🔐 Login attempt: {email}")

        # 🔴 basic validation
        if not email or not password:
            return render(request, 'login.html', {
                'error': 'Please enter email and password'
            })

        try:
            # 🔴 find client by email
            client = Client.objects.get(email=email)

            # 🔴 check password
            if client.password == password:
                print(f"✅ Login success: {client.name}")

                # ✅ ✅ ✅ SESSION STARTS HERE ✅ ✅ ✅
                request.session['client_id'] = client.id
                request.session['client_name'] = client.name
                # ✅ ✅ ✅ SESSION STORED ✅ ✅ ✅

                return redirect('home')

            else:
                print(f"❌ Wrong password: {email}")
                return render(request, 'login.html', {
                    'error': 'Invalid password'
                })

        except Client.DoesNotExist:
            print(f"❌ User not found: {email}")
            return render(request, 'login.html', {
                'error': 'Email not found'
            })

        except Exception as e:
            print(f"❌ Login error: {e}")
            return render(request, 'login.html', {
                'error': f'Login error: {str(e)}'
            })

    # 🔴 GET request → back to login
    return redirect('login')

def cancel_reservation(request, reservation_id):
    reservation = Reservation.objects.get(id=reservation_id)

    # تغییر وضعیت رزرو
    reservation.status = 'cancelled'
    reservation.save()

    # آزاد کردن ماشین
    car = reservation.car
    car.status = 'available'
    car.save()

    return redirect('reserve')

def edit(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)
    context = {
        'reservation': reservation,
        'is_edit': True
    }
    return render(request, 'booking.html', context)

def edit_submit(request, reservation_id):
    if request.method == 'POST':
        reservation = get_object_or_404(Reservation, id=reservation_id)
        start_date = parse_date(request.POST.get('start_date'))
        end_date = parse_date(request.POST.get('end_date'))

        if not start_date or not end_date:
            messages.error(request, "Please select valid dates.")
            return redirect('edit', reservation_id=reservation_id)
        if end_date < start_date:
            messages.error(request, "End date cannot be before start date.")
            return redirect('edit', reservation_id=reservation_id)

        reservation.start_date = start_date
        reservation.end_date = end_date
        reservation.save()
        messages.success(request, "Reservation updated successfully.")
        return redirect('reserve')
    return redirect('reserve')