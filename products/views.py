from datetime import timedelta
from django.db.models import Min, Max, Avg
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from products.models import Product, ShopProducts, PriceHistory, ProductsList
from products.serializers import (
    ProductListSerializer,
    ProductDetailSerializer,
    ShopPriceSerializer,
    PriceHistoryPointSerializer,
    PriceAlertCreateSerializer,
    ProductsListSerializer,
)
from services.trend import TrendCalculator
from services.currency.currency_conversion import CurrencyConversionService


class ProductListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProductListSerializer

    def get(self, request, *args, **kwargs):
        currency = request.query_params.get("currency", "USD")
        sort = request.query_params.get("sort", "price")
        order = request.query_params.get("order", "asc")

        products = Product.objects.annotate(
            price_min_usd=Min("shop_products__price_history__price_usd"),
            price_max_usd=Max("shop_products__price_history__price_usd"),
        )

        rows = []
        for product in products:
            price_min = self._convert(product.price_min_usd, currency)
            price_max = self._convert(product.price_max_usd, currency)
            rows.append({
                "id": product.id,
                "name": product.name,
                "price_min": price_min,
                "price_max": price_max,
                "currency": currency,
                "trend": TrendCalculator.calculate(product.id),
            })

        if sort == "price":
            rows.sort(key=lambda r: (r["price_min"] is None, r["price_min"]))
        elif sort == "trend":
            trend_order = {"falling": 0, "stable": 1, "rising": 2, None: 3}
            rows.sort(key=lambda r: trend_order.get(r["trend"], 3))

        if order == "desc":
            rows.reverse()

        serializer = self.get_serializer(rows, many=True)
        return Response(serializer.data)

    @staticmethod
    def _convert(amount_usd, currency_code):
        if amount_usd is None:
            return None
        return CurrencyConversionService.convert_from_usd(amount_usd, currency_code)


class ProductDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        currency = request.query_params.get("currency", "USD")

        agg = ShopProducts.objects.filter(product=product).aggregate(
            price_min_usd=Min("price_history__price_usd"),
            price_max_usd=Max("price_history__price_usd"),
        )
        price_min = self._convert(agg["price_min_usd"], currency)
        price_max = self._convert(agg["price_max_usd"], currency)

        data = {
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "price_min": price_min,
            "price_max": price_max,
            "currency": currency,
        }
        serializer = ProductDetailSerializer(data)
        return Response(serializer.data)

    @staticmethod
    def _convert(amount_usd, currency_code):
        if amount_usd is None:
            return None
        return CurrencyConversionService.convert_from_usd(amount_usd, currency_code)


class ProductPricesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        currency = request.query_params.get("currency", "USD")
        today = timezone.now().date()

        rows = []
        shop_products = ShopProducts.objects.filter(product=product).select_related("shop")
        for shop_product in shop_products:
            latest = (
                shop_product.price_history.filter(recorded_at=today)
                .order_by("-id")
                .first()
            )
            if latest is None:
                continue
            price = CurrencyConversionService.convert_from_usd(latest.price_usd, currency)
            rows.append({
                "shop": shop_product.shop.url_shop,
                "price": price,
                "currency": currency,
            })

        serializer = ShopPriceSerializer(rows, many=True)
        return Response(serializer.data)


class ProductPriceHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        currency = request.query_params.get("currency", "USD")
        date_from = request.query_params.get("date_from")
        date_to = request.query_params.get("date_to")

        history_qs = PriceHistory.objects.filter(shop_product__product=product)
        if date_from:
            history_qs = history_qs.filter(recorded_at__gte=date_from)
        if date_to:
            history_qs = history_qs.filter(recorded_at__lte=date_to)

        series = {}
        for entry in history_qs.select_related("shop_product__shop").order_by("recorded_at"):
            shop_name = entry.shop_product.shop.url_shop
            price = CurrencyConversionService.convert_from_usd(entry.price_usd, currency)
            series.setdefault(shop_name, []).append({"date": entry.recorded_at, "price": price})

        average = (
            history_qs.values("recorded_at")
            .annotate(avg_price=Avg("price_usd"))
            .order_by("recorded_at")
        )
        series["average"] = [
            {"date": row["recorded_at"], "price": CurrencyConversionService.convert_from_usd(row["avg_price"], currency)}
            for row in average
        ]

        result = {
            shop: PriceHistoryPointSerializer(points, many=True).data
            for shop, points in series.items()
        }
        return Response({"series": result})


class PriceAlertCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PriceAlertCreateSerializer

    def perform_create(self, serializer):
        product = get_object_or_404(Product, pk=self.kwargs["pk"])
        serializer.save(user=self.request.user, product=product)


class TrackProductView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        entry, created = ProductsList.objects.get_or_create(user=request.user, product=product)
        serializer = ProductsListSerializer(entry)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class TrackedProductsListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProductsListSerializer

    def get_queryset(self):
        return ProductsList.objects.filter(user=self.request.user).select_related("product")
