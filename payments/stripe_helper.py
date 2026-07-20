import stripe
from django.conf import settings
from django.urls import reverse

from payments.models import Payment, PaymentStatus


def create_stripe_session(borrowing, request, money_to_pay, payment_type):
    stripe.api_key = settings.STRIPE_KEY

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "unit_amount": int(money_to_pay * 100),
                    "product_data": {
                        "name": f"Borrowing: {borrowing.book.title}",
                    },
                },
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url=request.build_absolute_uri(
            reverse("payments:payment-success")
        )
        + "?session_id={CHECKOUT_SESSION_ID}",
        cancel_url=request.build_absolute_uri(
            reverse("payments:payment-cancel")
        ),
    )

    payment = Payment.objects.create(
        status=PaymentStatus.PENDING,
        type=payment_type,
        borrowing=borrowing,
        session_url=session.url,
        session_id=session.id,
        money_to_pay=money_to_pay,
    )
    return payment
