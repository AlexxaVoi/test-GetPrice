from celery import shared_task
from datetime import date, timedelta
from services.shop.dummyjson import DummyShopService
from services.shop.fakestoreapi import FakeStoreShopService
from services.shop.base import ProductImportService
from services.currency.nbu import NBUCurrencyService
from services.currency.history_nby import CurrencyRateSyncService
from products.models import PriceAlert, PriceHistory
from services.currency.currency_conversion import CurrencyConversionService
from services.email import send_price_alert_email


@shared_task
def sync_dummyjson_products():
    shop_data = DummyShopService().get_products()
    ProductImportService().save_products(shop_data)


@shared_task
def sync_fakestore_products():
    shop_data = FakeStoreShopService().get_products()
    ProductImportService().save_products(shop_data)


@shared_task
def sync_daily_exchange_rates():
    rates = NBUCurrencyService().get_rates(on_date=date.today())
    CurrencyRateSyncService.save_rates(rates, on_date=date.today())


@shared_task
def backfill_exchange_rates_for_year(year: int):
    day = date(year, 1, 1)
    end = date(year, 12, 31)
    while day <= end:
        rates = NBUCurrencyService().get_rates(on_date=day)
        CurrencyRateSyncService.save_rates(rates, on_date=day)
        day += timedelta(days=1)


@shared_task
def check_price_alerts():
    for alert in PriceAlert.objects.filter(is_active=True, is_sent=False).select_related("product", "currency", "user"):
        latest_prices = PriceHistory.objects.filter(
            shop_product__product=alert.product
        ).order_by("shop_product_id", "-recorded_at").distinct("shop_product_id")

        if not latest_prices:
            continue

        min_price_usd = min(p.price_usd for p in latest_prices)
        min_price_converted = CurrencyConversionService.convert_from_usd(
            min_price_usd, alert.currency.code
        )

        if min_price_converted <= alert.target_price:
            send_price_alert_email(alert.user.email, alert.product.name, min_price_converted, alert.currency.code)
            alert.is_sent = True
            alert.save(update_fields=["is_sent"])
