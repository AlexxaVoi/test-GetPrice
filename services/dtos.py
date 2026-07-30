from dataclasses import dataclass
from decimal import Decimal


@dataclass
class ExternalProduct:
    external_id: str
    name: str
    description: str
    price: Decimal


@dataclass
class ShopData:
    url_shop: str
    data_shop: list[ExternalProduct]


@dataclass
class ExternalRate:
    code: str
    rate_to_uah: Decimal