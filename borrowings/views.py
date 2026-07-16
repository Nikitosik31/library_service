from datetime import date

from django.db import transaction
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.mixins import (
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
)
from rest_framework.permissions import IsAuthenticated

from borrowings.models import Borrowing
from borrowings.serializers import (
    BorrowingsSerializer,
    BorrowingsCreateSerializer,
)
from notifications.telegram_helper import send_telegram_notification
import logging

logger = logging.getLogger(__name__)


class BorrowingsViewSet(
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Borrowing.objects.select_related("user", "book")
    serializer_class = BorrowingsSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = Borrowing.objects.select_related("user", "book")

        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)

        is_active = self.request.query_params.get("is_active")
        if is_active == "true":
            queryset = queryset.filter(actual_return_date__isnull=True)
        user_id = self.request.query_params.get("user_id")
        if user_id and self.request.user.is_staff:
            queryset = queryset.filter(user_id=user_id)

        return queryset

    def get_serializer_class(self):
        if self.action == "create":
            return BorrowingsCreateSerializer
        return BorrowingsSerializer

    def perform_create(self, serializer):
        with transaction.atomic():
            book = serializer.validated_data["book"]
            book.inventory -= 1
            book.save()
            borrowing = serializer.save(user=self.request.user)

        text = (
            f"📚 New borrowing created!\n\n"
            f"User: {borrowing.user.email}\n"
            f"Book: {borrowing.book.title}\n"
            f"Borrow date: {borrowing.borrow_date}\n"
            f"Expected return: {borrowing.expected_return_date}"
        )
        try:
            send_telegram_notification(text)
        except Exception:
            logger.exception("Failed to send Telegram notification")

    @action(
        detail=True, methods=["post"], url_name="return", url_path="return"
    )
    def borrowing_return(self, request, pk=None):
        borrowing = self.get_object()
        if borrowing.actual_return_date:
            raise ValidationError("This borrowing has already been returned.")
        with transaction.atomic():
            borrowing.actual_return_date = date.today()
            borrowing.save()
            borrowing.book.inventory += 1
            borrowing.book.save()

        return Response(
            {"detail": "Book returned successfully."},
            status=status.HTTP_200_OK,
        )
