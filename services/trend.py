from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from django.db.models import Avg
from products.models import PriceHistory


class TrendCalculator:
    RISING, FALLING, STABLE = "rising", "falling", "stable"
    THRESHOLD_PERCENT = Decimal("1.0")  

    @classmethod
    def calculate(cls, product_id: int) -> str | None:
        today = timezone.now().date()
        today_avg = PriceHistory.objects.filter(
            shop_product__product_id=product_id, recorded_at=today
        ).aggregate(avg=Avg("price_usd"))["avg"]

        past_avg = PriceHistory.objects.filter(
            shop_product__product_id=product_id,
            recorded_at__gte=today - timedelta(days=30),
            recorded_at__lt=today,
        ).aggregate(avg=Avg("price_usd"))["avg"]

        if today_avg is None or past_avg is None or past_avg == 0:
            return None

        diff_percent = (today_avg - past_avg) / past_avg * 100
        if diff_percent > cls.THRESHOLD_PERCENT:
            return cls.RISING
        if diff_percent < -cls.THRESHOLD_PERCENT:
            return cls.FALLING
        return cls.STABLE