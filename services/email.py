import logging
from decimal import Decimal
from django.core.mail import send_mail
from django.conf import settings


logger = logging.getLogger(__name__)


def send_price_alert_email(to_email: str, product_name: str, price: Decimal, currency_code: str) -> None:
    subject = f"Price alert: {product_name}"
    message = (
        f"The price of '{product_name}' has dropped to {price} {currency_code}, "
        f"which meets your alert threshold."
    )
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
            recipient_list=[to_email],
            fail_silently=False,
        )
    except Exception as e:
        logger.error(f"Failed to send price alert email to {to_email}: {e}")
