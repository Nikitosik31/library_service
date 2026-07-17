from django.urls import path, include
from rest_framework import routers

from payments.views import PaymentViewSet

router = routers.DefaultRouter()
router.register("payments", PaymentViewSet)

app_name = "payments"
urlpatterns = [
    path("", include(router.urls)),
]
