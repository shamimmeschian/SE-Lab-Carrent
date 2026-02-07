
from django.db import models
from django.core.validators import MinValueValidator  
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
class Client(models.Model):
    name = models.CharField(max_length=100)
    password = models.CharField(max_length=128)
    phone = models.CharField(max_length=15)
    email = models.EmailField(unique=True)  
    
    def __str__(self):
        return f"{self.name} ({self.email})"
    
class Car(models.Model):
    model = models.CharField(max_length=100)
    
    FUEL_CHOICES = [
        ('petrol', 'Petrol'),
        ('diesel', 'Diesel'),
        ('electric', 'Electric'),
    ]
    fuel = models.CharField(max_length=10, choices=FUEL_CHOICES)
    
    TRANSMISSION_CHOICES = [
        ('manual', 'Manual'),
        ('automatic', 'Automatic'),
    ]
    transmission = models.CharField(max_length=10, choices=TRANSMISSION_CHOICES)
    
    price_per_day = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0.01, _("Price must be greater than zero"))]
    )
    
    capacity = models.PositiveIntegerField(
        help_text=_("Number of passengers"),
        validators=[MinValueValidator(1, _("Capacity must be at least 1"))]
    )
    
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('rented', 'Rented'),
        ('maintenance', 'Maintenance'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    
    def __str__(self):
        return f"{self.model}"
    
    def clean(self):
        """اعتبارسنجی اضافی"""
        if self.price_per_day <= 0:
            raise ValidationError({'price_per_day': _("Price must be positive")})
        
        if self.capacity <= 0:
            raise ValidationError({'capacity': _("Capacity must be positive")})

class Reservation(models.Model):
    customer = models.ForeignKey(Client, on_delete=models.CASCADE)
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    
    start_date = models.DateField()
    end_date = models.DateField()
    
    total_price = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        blank=True, 
        null=True,
        validators=[MinValueValidator(0)]
    )
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # با default موقت اضافه کن
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @staticmethod
    def is_car_available(car, start_date, end_date):
        return not Reservation.objects.filter(
            car=car,
            status__in=['pending', 'confirmed']
        ).filter(
            Q(start_date__lte=end_date) &
            Q(end_date__gte=start_date)
        ).exists()
    
    def clean(self):
        """اعتبارسنجی تاریخ‌ها"""
        errors = {}
        
        if self.end_date and self.start_date:
            if self.end_date < self.start_date:
                errors['end_date'] = _("End date cannot be before start date")
        
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()

        if self.car and self.car.price_per_day:
            days = (self.end_date - self.start_date).days + 1
            self.total_price = self.car.price_per_day * days

        super().save(*args, **kwargs)   

    
    def __str__(self):
        return f"Reservation #{self.id} - {self.customer.email}"
    
    @property
    def total_days(self):
        """تعداد روزهای رزرو"""
        if self.end_date and self.start_date:
            return (self.end_date - self.start_date).days + 1
        return 0
    
class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.email}"