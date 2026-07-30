from rest_framework import serializers


class ExternalProductSerializer(serializers.Serializer):
    external_id = serializers.CharField()
    name = serializers.CharField()
    description = serializers.CharField(allow_blank=True)
    price = serializers.DecimalField(max_digits=10, decimal_places=2)