from django.urls import path
from products import views

urlpatterns = [
    path("products/", views.ProductListView.as_view(), name="product-list"),
    path("products/tracked/", views.TrackedProductsListView.as_view(), name="product-tracked"),
    path("products/<int:pk>/", views.ProductDetailView.as_view(), name="product-detail"),
    path("products/<int:pk>/prices/", views.ProductPricesView.as_view(), name="product-prices"),
    path("products/<int:pk>/price-history/", views.ProductPriceHistoryView.as_view(), name="product-price-history"),
    path("products/<int:pk>/alerts/", views.PriceAlertCreateView.as_view(), name="product-alert-create"),
    path("products/<int:pk>/track/", views.TrackProductView.as_view(), name="product-track"),
]
