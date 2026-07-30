from decimal import Decimal
from currency.models import Currency, ExchangeRate


class CurrencyConversionService:
    @staticmethod
    def convert_from_usd(amount_usd: Decimal, target_code: str, on_date=None) -> Decimal:
        if target_code == "USD":
            return amount_usd

        usd_rate = ExchangeRate.objects.filter(
            currency__code="USD", **({"date": on_date} if on_date else {})
        ).order_by("-date").first()
        amount_uah = amount_usd * usd_rate.rate_to_uah

        if target_code == "UAH":
            return amount_uah

        target_rate = ExchangeRate.objects.filter(
            currency__code=target_code, **({"date": on_date} if on_date else {})
        ).order_by("-date").first()
        return amount_uah / target_rate.rate_to_uah
