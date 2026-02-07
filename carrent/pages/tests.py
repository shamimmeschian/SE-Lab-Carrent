from django.test import TestCase
from django.test import TestCase, Client
from django.urls import reverse
from pages.models import Client as MyClient, Car, Reservation

class RentalFlowTest(TestCase):
    def setUp(self):
        # ایجاد داده نمونه
        self.client = Client()
        self.user = MyClient.objects.create(
            name="Test User", email="t@example.com", phone="0900", password="1234"
        )
        self.car = Car.objects.create(
            model="Toyota", fuel="petrol",
            transmission="manual", price_per_day=100, capacity=4, status="available"
        )

    def test_registration_success(self):
        resp = self.client.post(reverse("register_submit"), {
            "name": "Ali",
            "email": "a@a.com",
            "phone": "123",
            "password": "1",
            "confirm_password": "1",
        })
        self.assertEqual(resp.status_code, 302)  # redirect
        self.assertTrue(MyClient.objects.filter(email="a@a.com").exists())

    def test_login_success(self):
        resp = self.client.post(reverse("login_submit"), {
            "email": "t@example.com", "password": "1234"
        })
        self.assertEqual(resp.status_code, 302)  # redirect to home

    def test_booking_page_renders(self):
        resp = self.client.get(reverse("booking"))
        self.assertEqual(resp.status_code, 200)

    def test_car_status_validation(self):
        self.car.price_per_day = 0
        with self.assertRaises(Exception):
            self.car.full_clean()

    def test_reservation_price_auto_calculate(self):
        # ایجاد رزرو با تاریخ معتبر
        start = "2026-02-01"
        end = "2026-02-03"
        res = Reservation.objects.create(
            customer=self.user, car=self.car,
            start_date=start, end_date=end, status="pending"
        )
        self.assertEqual(float(res.total_price), 300.0)

    def test_home_page_render(self):
        resp = self.client.get(reverse("home"))
        self.assertEqual(resp.status_code, 200)

# Create your tests here.
