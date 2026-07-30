from rest_framework import serializers
from currency.models import Currency
from products.models import Product, PriceAlert, ProductsList


class ProductListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    price_min = serializers.DecimalField(max_digits=12, decimal_places=2, allow_null=True)
    price_max = serializers.DecimalField(max_digits=12, decimal_places=2, allow_null=True)
    currency = serializers.CharField()
    trend = serializers.CharField(allow_null=True)


class ProductDetailSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    description = serializers.CharField(allow_blank=True)
    price_min = serializers.DecimalField(max_digits=12, decimal_places=2, allow_null=True)
    price_max = serializers.DecimalField(max_digits=12, decimal_places=2, allow_null=True)
    currency = serializers.CharField()


class ShopPriceSerializer(serializers.Serializer):
    shop = serializers.CharField()
    price = serializers.DecimalField(max_digits=12, decimal_places=2)
    currency = serializers.CharField()


class PriceHistoryPointSerializer(serializers.Serializer):
    date = serializers.DateField()
    price = serializers.DecimalField(max_digits=12, decimal_places=2)


class PriceAlertCreateSerializer(serializers.ModelSerializer):
    currency = serializers.SlugRelatedField(slug_field="code", queryset=Currency.objects.all())

    class Meta:
        model = PriceAlert
        fields = ["id", "currency", "target_price", "is_active", "created_at"]
        read_only_fields = ["id", "is_active", "created_at"]


class ProductsListSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(source="product.id", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = ProductsList
        fields = ["id", "product_id", "product_name"]
