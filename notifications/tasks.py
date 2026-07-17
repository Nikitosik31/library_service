from datetime import timedelta, date

from celery import shared_task

from borrowings.models import Borrowing
from notifications.telegram_helper import send_telegram_notification


@shared_task
def check_overdue_borrowings():
    tomorrow = date.today() + timedelta(days=1)

    overdue = Borrowing.objects.filter(
        expected_return_date__lte=tomorrow,
        actual_return_date__isnull=True,
    ).select_related("user", "book")

    if not overdue.exists():
        send_telegram_notification("No borrowings overdue today")
        return "No overdue borrowings"

    count = 0

    for borrowing in overdue:
        text = (
            f"⚠️ Overdue borrowing!\n\n"
            f"User: {borrowing.user.email}\n"
            f"Book: {borrowing.book.title}\n"
            f"Borrow date: {borrowing.borrow_date}\n"
            f"Expected return: {borrowing.expected_return_date}"
        )

        send_telegram_notification(text)
        count += 1

    return f"Sent {count} overdue notification"
