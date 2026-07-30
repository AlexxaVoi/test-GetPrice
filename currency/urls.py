from django.urls import path
from currency import views

urlpatterns = [
    path("currencies/", views.CurrencyListView.as_view(), name="currency-list"),
]
