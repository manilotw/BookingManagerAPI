from datetime import date

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from rooms.models import Booking, Room


class BookingTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="password123"
        )
        self.room = Room.objects.create(name="Room 1", price_per_day=100, capacity=2)

    def test_create_booking(self):
        self.client.login(username="testuser", password="password123")

        response = self.client.post(
            reverse("booking-list"),
            {
                "room": self.room.id,
                "start_date": date(2026, 3, 1),
                "end_date": date(2026, 3, 5),
            },
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_prevent_double_booking(self):
        Booking.objects.create(
            room=self.room,
            user=self.user,
            start_date=date(2026, 3, 1),
            end_date=date(2026, 3, 5),
        )

        self.client.login(username="testuser", password="password123")

        response = self.client.post(
            reverse("booking-list"),
            {
                "room": self.room.id,
                "start_date": date(2026, 3, 2),
                "end_date": date(2026, 3, 4),
            },
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
