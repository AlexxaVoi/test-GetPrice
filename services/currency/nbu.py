from config.settings import CURRENCY_CODE_LIST, NBU_API, FROM_2025_NBU_API
from requests import HTTPError, ConnectionError, Timeout
from datetime import date as date_type
from services.dtos import ExternalRate 
import requests
import logging


logger = logging.getLogger(__name__)


class NBUCurrencyService():

    def get_rates(self, on_date: date_type | None = None) -> list[ExternalRate]:
        params = {"json": ""}
        if on_date:
            params["date"] = on_date.strftime("%Y%m%d")
        try:
            response = requests.get(NBU_API, params=params, timeout=10)
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

        return [
            ExternalRate(
                code=item.get("cc"), 
                rate_to_uah=item.get("rate")
            )
            for item in response.json()
            if item.get("cc") in CURRENCY_CODE_LIST
        ]
        
