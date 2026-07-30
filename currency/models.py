from django.db import models
from django.core.validators import MinValueValidator

# remove 
class Currency(models.Model):
    code = models.CharField(max_length=3, unique=True, help_text="ex: USD")
    name = models.CharField(max_length=50)

class ExchangeRate(models.Model):
    currency = models.ForeignKey(
        Currency, 
        on_delete=models.CASCADE,
        related_name="exchange_rates"
    )
    rate_to_uah = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        validators=[MinValueValidator(0)]
    )
    date = models.DateField(db_index=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["currency", "date"], name="unique_currency_date")
        ]
        ordering = ["-date"]


    