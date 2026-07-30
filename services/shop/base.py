from abc import ABC, abstractmethod
from services.dtos import ShopData, ExternalProduct
from products.models import Shop, Product, ShopProducts, PriceHistory
from django.db import transaction
from decimal import Decimal
import logging


logger = logging.getLogger(__name__)


class BaseShopServive(ABC):

    @abstractmethod
    def get_products(self):
        pass

class ProductImportService:

    @staticmethod
    def save_shop(url_shop: str):
        shop, _ = Shop.objects.get_or_create(url_shop = url_shop) 
        return shop

    @staticmethod
    def save_product(item: ExternalProduct):
        product, _ = Product.objects.get_or_create(
            name = item.name,
            defaults={
                'description': item.description
            }  
        )
        return product

    @staticmethod
    def save_shop_products(shop_id, product_id, item: ExternalProduct):
        shop_products, _ =  ShopProducts.objects.get_or_create(
            shop = shop_id, external_id = item.external_id,
            defaults={"product": product_id},
        )
        return shop_products

    @staticmethod
    def save_price_history(shop_products_id, item: ExternalProduct):
        return PriceHistory.objects.create(
            shop_product = shop_products_id,
            price_usd = Decimal(str(item.price)),
        )
    
    def save_products(self, shop_data: ShopData)-> None:
        try:
            shop = self.save_shop(shop_data.url_shop)
        except Exception as e:
            logger.error(f"The shop has not been saved: {e}")
            return
        for item in shop_data.data_shop:
            try:
                with transaction.atomic():
                    product = self.save_product(item)
                    shop_products = self.save_shop_products(shop_id=shop, product_id=product, item=item)
                    self.save_price_history(shop_products_id=shop_products, item=item)
            except Exception as e:
                logger.warning(f"The product {item.name} was omitted due to an error: {e}")
