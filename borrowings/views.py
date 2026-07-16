from django.shortcuts import render
from rest_framework import viewsets

from borrowings.models import Borrowing
from borrowings.serializers import BorrowingsSerializer


class BorrowingsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Borrowing.objects.select_related("user", "book")
    serializer_class = BorrowingsSerializer
