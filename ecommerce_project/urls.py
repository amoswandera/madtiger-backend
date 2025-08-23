# ecommerce_project/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings           # Import settings
from django.conf.urls.static import static # Import static
from website.views import ProductAPIView
from website.views import ProductAPIView, ProductDetailAPIView
from website.views import ProductAPIView, ProductDetailAPIView, CategoryListAPIView
from website.views import RegisterView, CustomAuthToken
from website.views import OrderCreateAPIView
from website.views import OrderCreateAPIView
from website.views import OrderListAPIView
from website.views import CreatePaymentIntentView
from website.views import AllProductsAPIView
from website.views import CollectionListView, CollectionDetailView
from website.views import OrderCancelAPIView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('website.urls')),
    path('api/products/', ProductAPIView.as_view(), name='product-api'),
    path('api/products/<int:pk>/', ProductDetailAPIView.as_view(), name='product-api-detail'),
    path('api/categories/', CategoryListAPIView.as_view(), name='category-api-list'),
    path('api/register/', RegisterView.as_view(), name='api-register'),
    path('api/login/', CustomAuthToken.as_view(), name='api-login'),
    path('api/orders/create/', OrderCreateAPIView.as_view(), name='order-create-api'),
    path('api/orders/', OrderListAPIView.as_view(), name='order-list-api'),
    path('api/create-payment-intent/', CreatePaymentIntentView.as_view(), name='create-payment-intent'),
    path('api/products/all/', AllProductsAPIView.as_view(), name='all-products-api'),
    path('api/collections/', CollectionListView.as_view(), name='collection-list-api'),
    path('api/collections/<slug:slug>/', CollectionDetailView.as_view(), name='collection-detail-api'),
    path('api/orders/<int:pk>/cancel/', OrderCancelAPIView.as_view(), name='order-cancel-api'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)