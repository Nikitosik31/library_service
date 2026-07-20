from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from books.tests.helper import sample_user, sample_book
from borrowings.models import Borrowing

BORROWING_URL = reverse("borrowings:borrowing-list")


class AuthenticatedBorrowingApiTest(APITestCase):
    def setUp(self):
        self.user = sample_user(is_staff=False)
        self.client.force_authenticate(self.user)
        self.book = sample_book(inventory=5)

    def test_create_borrowing_attaches_user(self):
        payload = {
            "book": self.book.id,
            "expected_return_date": "2026-08-01",
        }
        res = self.client.post(BORROWING_URL, payload)
        borrowing = Borrowing.objects.get(book=self.book)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(borrowing.user, self.user)

    def test_cannot_borrow_out_of_stock(self):
        book = sample_book(inventory=0)
        payload = {
            "book": book.id,
            "expected_return_date": "2026-08-01",
        }
        res = self.client.post(BORROWING_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_sees_only_own_borrowings(self):
        Borrowing.objects.create(
            user=self.user, book=self.book, expected_return_date="2026-08-01"
        )
        user2 = sample_user(email="user2@example")
        Borrowing.objects.create(
            user=user2, book=self.book, expected_return_date="2026-08-01"
        )
        res = self.client.get(BORROWING_URL)
        self.assertEqual(len(res.data), 1)

    def test_filter_by_is_active(self):
        Borrowing.objects.create(
            user=self.user, book=self.book, expected_return_date="2026-08-01"
        )
        Borrowing.objects.create(
            user=self.user,
            book=self.book,
            expected_return_date="2026-08-01",
            actual_return_date="2026-08-11",
        )
        res = self.client.get(BORROWING_URL, {"is_active": "true"})
        self.assertEqual(len(res.data), 1)

    def test_return_increases_inventory(self):
        borrowing = Borrowing.objects.create(
            user=self.user, book=self.book, expected_return_date="2026-08-01"
        )
        url = reverse("borrowings:borrowing-return", args=[borrowing.id])
        inventory_before = self.book.inventory

        res = self.client.post(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.book.refresh_from_db()
        self.assertEqual(self.book.inventory, inventory_before + 1)
        borrowing.refresh_from_db()
        self.assertIsNotNone(borrowing.actual_return_date)

    def test_cannot_return_twice(self):
        borrowing = Borrowing.objects.create(
            user=self.user, book=self.book, expected_return_date="2026-08-01"
        )
        url = reverse("borrowings:borrowing-return", args=[borrowing.id])
        self.client.post(url)
        res = self.client.post(url)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


class AdminBorrowingApiTest(APITestCase):
    def setUp(self):
        self.user = sample_user(is_staff=True)
        self.client.force_authenticate(self.user)
        self.book = sample_book(inventory=5)

    def test_admin_sees_all_borrowings(self):
        user2 = sample_user(email="user2@example")
        Borrowing.objects.create(
            user=self.user, book=self.book, expected_return_date="2026-08-01"
        )
        Borrowing.objects.create(
            user=user2, book=self.book, expected_return_date="2026-08-01"
        )
        res = self.client.get(BORROWING_URL)
        self.assertEqual(len(res.data), 2)

    def test_admin_filter_by_user_id(self):
        user2 = sample_user(email="user2@example")
        Borrowing.objects.create(
            user=self.user, book=self.book, expected_return_date="2026-08-01"
        )
        Borrowing.objects.create(
            user=user2, book=self.book, expected_return_date="2026-08-01"
        )
        res = self.client.get(BORROWING_URL, {"user_id": self.user.id})
        self.assertEqual(len(res.data), 1)
