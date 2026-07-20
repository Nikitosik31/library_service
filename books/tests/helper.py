import uuid
from datetime import timedelta, date

from django.contrib.auth import get_user_model

from books.models import Book
from borrowings.models import Borrowing
from payments.models import PaymentStatus, PaymentType, Payment


def sample_user(**params):
    defaults = {
        "email": f"user_{uuid.uuid4().hex[:8]}@test.com",
        "first_name": "Lala",
        "last_name": "Lala",
        "password": "testetss",
        "is_staff": True,
    }
    defaults.update(params)
    return get_user_model().objects.create_user(**defaults)


def sample_book(**params):
    defaults = {
        "title": "Book Title",
        "author": "Author",
        "cover": "Hard",
        "inventory": 5,
        "daily_fee": "2.50",
    }
    defaults.update(params)
    return Book.objects.create(**defaults)


def sample_borrowing(**params):
    defaults = {
        "expected_return_date": date.today() + timedelta(days=7),
        "book": sample_book(),
    }
    defaults.update(params)
    return Borrowing.objects.create(**defaults)


def sample_payment(**params):
    defaults = {
        "status": PaymentStatus.PENDING,
        "type": PaymentType.PAYMENT,
        "borrowing": sample_borrowing(user=sample_user()),
        "session_url": "https://checkout.stripe.com/test",
        "session_id": "cs_test_fake",
        "money_to_pay": "10.00",
    }
    defaults.update(params)
    return Payment.objects.create(**defaults)
