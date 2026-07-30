from django.contrib import admin
from products.models import Shop, Product, ShopProducts, ProductsList, PriceHistory, PriceAlert

admin.site.register(Shop)
admin.site.register(Product)
admin.site.register(ShopProducts)
admin.site.register(ProductsList)
admin.site.register(PriceHistory)
admin.site.register(PriceAlert)
