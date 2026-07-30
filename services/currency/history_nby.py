from currency.models import Currency, ExchangeRate
from services.dtos import ExternalRate


class CurrencyRateSyncService:
    @staticmethod
    def save_rates(rates: list[ExternalRate], on_date) -> None:
        for item in rates:
            try:
                currency = Currency.objects.get(code=item.code)
            except Currency.DoesNotExist:
                continue
            ExchangeRate.objects.update_or_create(
                currency=currency, date=on_date,
                defaults={"rate_to_uah": item.rate_to_uah},
            )
