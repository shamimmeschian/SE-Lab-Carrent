
from django.contrib import admin
from django.urls import path
from pages.views import *


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('home', home, name='home'),
    path("booking",booking, name="booking"),
    path('cars', cars, name='cars'),
    path('confirm', confirm, name='confirm'),
    path('contact', contact, name='contact'),
    path('edit', edit, name='edit'),
    path('login', login, name='login'),
    path('reserve', reserve, name='reserve'),
    path('register', register, name='register'),
    path('success/<int:reservation_id>/', success, name='success'),
    path('register/submit/', register_submit, name='register_submit'),
    path('login/submit/', login_submit, name='login_submit'), 
    path('cancel/<int:reservation_id>/', cancel_reservation, name='cancel_reservation'),
    path('edit/<int:reservation_id>/', edit, name='edit'),
    path('edit/submit/<int:reservation_id>/', edit_submit, name='edit_submit'),
    path('logout', logout, name='logout'),

]
