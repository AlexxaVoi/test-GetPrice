from django.db import models
from django.core.validators import MinValueValidator
from currency.models import Currency
from users.models import User

class Shop(models.Model):
    name = models.CharField(max_length=255)
    url_shop = models.URLField(unique=True)

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

class ShopProducts(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name="shop_products")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="shop_products")
    external_id = models.CharField(max_length=100, help_text="The product ID in this shop")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["shop", "external_id"],
                name="unique_external_product"
            )
        ]

class ProductsList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "product"], name="unique_user_product")
        ]


class PriceHistory(models.Model):
    shop_product = models.ForeignKey(ShopProducts, on_delete=models.CASCADE, related_name="price_history")
    price_usd = models.DecimalField( ## int - save in центах
        max_digits=10,
        decimal_places=4,
        validators=[MinValueValidator(0)]
    )
    recorded_at = models.DateTimeField(auto_now_add=True, db_index=True) # created_at

    class Meta:
        ordering = ["-recorded_at", "shop_product",]
        indexes = [models.Index(fields=["shop_product", "-recorded_at"])]

class PriceAlert(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="price_alerts"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="alerts"
    )
    currency = models.ForeignKey(
        Currency,
        on_delete=models.PROTECT
    )
    target_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    is_active = models.BooleanField(default=True)
    is_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)