from .base import BaseShopServive
from config.settings import FAKESTORE_SHOP_API
from requests import ConnectionError, Timeout, HTTPError
from services.dtos import ShopData, ExternalProduct
from services.serializers import ExternalProductSerializer
import requests
import logging


logger = logging.getLogger(__name__)


class FakeStoreShopService(BaseShopServive):
    shop_name = "fakestoreapi"

    def get_products(self) -> list[ExternalProduct]:
        try:
            response = requests.get(FAKESTORE_SHOP_API, timeout=10)
            response.raise_for_status()
        except Timeout:
                    logger.error("The server is responding too slowly (Timeout)")
                    return []
        except ConnectionError:
            logger.error("There is no connection to the server or network (ConnectionError)")
            return []
        except HTTPError as err:
            logger.error(f"The server returned an HTTP error: {err.response.status_code}")
            return []

        raw_products = response.json()
        normalized = [
            {
                "external_id": str(p.get("id")),
                "name": p.get("title"),
                "description": p.get("description", ""),
                "price": p.get("price"),
            }
            for p in raw_products
        ]

        serializer = ExternalProductSerializer(data=normalized, many=True)
        serializer.is_valid(raise_exception=False)

        products = [
            ExternalProduct(**item) for item in serializer.validated_data
        ]
        if len(products) < len(normalized):
            logger.warning(
                f"{len(normalized) - len(products)} products from {self.shop_name} "
                f"failed validation and were skipped: {serializer.errors}"
            )
        
        return ShopData(
            url_shop=FAKESTORE_SHOP_API,
            data_shop=products
        )