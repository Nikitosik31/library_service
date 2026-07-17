from datetime import date

from rest_framework import serializers

from books.serializers import BookSerializer
from borrowings.models import Borrowing


class BorrowingsSerializer(serializers.ModelSerializer):
    book = BookSerializer()

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
        )


class BorrowingsCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "book",
        )

    def validate_book(self, value):
        if value.inventory < 1:
            raise serializers.ValidationError("This book is not available")
        return value

    def validate(self, attrs):
        if attrs.get("expected_return_date") <= date.today():
            raise serializers.ValidationError(
                {
                    "expected_return_date": "Expected return date must be later than today."
                }
            )
        return attrs
