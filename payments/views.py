import stripe
from django.conf import settings
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import IsAuthenticated

from payments.models import Payment, PaymentStatus
from payments.serializers import PaymentSerializer


class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Payment.objects.select_related("borrowing")
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Payment.objects.select_related("borrowing")
        if not self.request.user.is_staff:
            queryset = queryset.filter(borrowing__user=self.request.user)
        return queryset

    def get_permissions(self):
        if self.action == "success":
            return []
        if self.action == "cancel":
            return []
        return [
            IsAuthenticated(),
        ]

    @action(detail=False, methods=["get"], url_path="cancel")
    def cancel(self, request):
        return Response(
            {
                "message": "Payment can be paid later. "
                "The session is available for 24 hours."
            }
        )

    @action(detail=False, methods=["get"], url_path="success")
    def success(self, request, *args, **kwargs):
        stripe.api_key = settings.STRIPE_KEY

        session_id = request.query_params.get("session_id")
        if session_id:
            session_retrieve = stripe.checkout.Session.retrieve(session_id)
            if session_retrieve.payment_status == "paid":
                payment = Payment.objects.get(session_id=session_id)
                payment.status = PaymentStatus.PAID
                payment.save()

                return Response({"payment_status": "Paid"})
            return Response(
                {"detail": "Payment not completed yet."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            {"detail": "Payment not completed yet."},
            status=status.HTTP_400_BAD_REQUEST,
        )
