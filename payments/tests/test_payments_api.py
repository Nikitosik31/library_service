from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from books.tests.helper import (
    sample_user,
    sample_book,
    sample_borrowing,
    sample_payment,
)

PAYMENTS_URL = reverse("payments:payment-list")


class UnauthorizedUser(APITestCase):
    def test_read_payments_list(self):
        response = self.client.get(PAYMENTS_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthorizedUser(APITestCase):
    def setUp(self):
        self.user = sample_user(is_staff=False)
        self.book = sample_book()
        self.client.force_authenticate(user=self.user)
        self.borrowing = sample_borrowing(user=self.user, book=self.book)
        self.payment = sample_payment(borrowing=self.borrowing)

    def test_user_seeing_owner(self):
        user2 = sample_user(email="vmcdsk@dsc.com", is_staff=False)
        borrowing2 = sample_borrowing(user=user2, book=self.book)
        payment2 = sample_payment(borrowing=borrowing2)

        response = self.client.get(PAYMENTS_URL)
        ids = [p["id"] for p in response.data]
        self.assertIn(self.payment.id, ids)
        self.assertNotIn(payment2.id, ids)
