from django.contrib import admin
from django.contrib import admin
from .models import Client, Car, Reservation,ContactMessage

# ثبت مدل‌ها در ادمین
admin.site.register(Client)
admin.site.register(Car)
admin.site.register(Reservation)
admin.site.register(ContactMessage)