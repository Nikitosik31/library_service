from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from books.tests.helper import sample_user

BOOK_URL = reverse("books:book-list")


class UnauthenticatedUserTest(APITestCase):
    def test_read_book_list(self):
        res = self.client.get(BOOK_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_book_anonymous(self):
        payload = {
            "title": "Test Book",
            "author": "Test Author",
            "cover": "Hard",
            "inventory": 5,
            "daily_fee": "1.50",
        }
        res = self.client.post(BOOK_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedUserTest(APITestCase):
    def setUp(self):
        self.user = sample_user(is_staff=False)
        self.client.force_authenticate(user=self.user)

    def test_create_book_forbidden(self):
        payload = {
            "title": "Test Book",
            "author": "Test Author",
            "cover": "Hard",
            "inventory": 5,
            "daily_fee": "1.50",
        }
        res = self.client.post(BOOK_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminBookApiTest(APITestCase):
    def setUp(self):
        self.user = sample_user(is_staff=True)
        self.client.force_authenticate(user=self.user)

    def test_create_book(self):
        payload = {
            "title": "Test Book",
            "author": "Test Author",
            "cover": "Hard",
            "inventory": 5,
            "daily_fee": "1.50",
        }
        res = self.client.post(BOOK_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
