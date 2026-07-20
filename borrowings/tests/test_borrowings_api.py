from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from books.tests.helper import sample_user, sample_book, sample_borrowing

BORROWING_URL = reverse("borrowings:borrowing-list")


class UnauthorizedUserTest(APITestCase):
    def test_unauthorized_user(self):
        response = self.client.get(BORROWINGS_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedBorrowingApiTest(APITestCase):
    def setUp(self):
        self.user = sample_user()
        self.client.force_authenticate(self.user)
        self.book = sample_book(inventory=5)

    def test_create_borrowing_decreases_inventory(self):
        payload = {
            "book": self.book.id,
            "expected_return_date": "2026-08-01",
        }
        res = self.client.post(BORROWING_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.book.refresh_from_db()
        self.assertEqual(self.book.inventory, 4)

    def test_create_borrowing_attaches_user(self):
