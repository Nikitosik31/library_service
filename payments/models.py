from django.db import models
from borrowings.models import Borrowing


class PaymentStatus(models.TextChoices):
    PENDING = "Pending"
    PAID = "Paid"


class PaymentType(models.TextChoices):
    PAYMENT = "Payment"
    FINE = "Fine"


class Payment(models.Model):
    status = models.CharField(
        max_length=10,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
    )
    type = models.CharField(max_length=10, choices=PaymentType.choices)
    borrowing = models.ForeignKey(
        Borrowing, on_delete=models.CASCADE, related_name="payments"
    )
    session_url = models.URLField(max_length=1000, null=True, blank=True)
    session_id = models.CharField(max_length=255, null=True, blank=True)
    money_to_pay = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.type + " " + self.status
