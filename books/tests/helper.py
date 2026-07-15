from django.contrib.auth import get_user_model

from books.models import Book


def sample_user(**params):
    defaults = {
        "email": "lala@lal.com",
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
