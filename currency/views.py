from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from currency.models import Currency
from currency.serializers import CurrencySerializer


class CurrencyListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer
