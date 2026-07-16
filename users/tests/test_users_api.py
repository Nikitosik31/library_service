from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

REGISTRATION_URL = reverse("users:create")


class UserManagerTestApi(APITestCase):
    def test_create_user(self):
        res = self.client.post(
            REGISTRATION_URL,
            {"email": "test@test.com", "password": "testtest"},
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["is_staff"], False)
        user = get_user_model().objects.get(email="test@test.com")
        self.assertEqual(user.check_password("testtest"), True)

    def test_create_user_without_email(self):
        res = self.client.post(
            REGISTRATION_URL,
            {"email": "", "password": "hbjnlkm"},
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
