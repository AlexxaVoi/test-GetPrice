from django.contrib import admin
from currency.models import Currency, ExchangeRate

admin.site.register(Currency)
admin.site.register(ExchangeRate)
