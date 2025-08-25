# ecommerce_project/urls.py (Final, Simplified, and Correct Version)

from django.contrib import admin
from django.urls import path

# Import all your views in a clean, grouped block
from website.views import (
    ProductAPIView, 
    ProductDetailAPIView, 
    CategoryListAPIView, 
    RegisterView, 
    CustomAuthToken, 
    OrderCreateAPIView, 
    OrderListAPIView,
    OrderCancelAPIView,
    AllProductsAPIView,
    CollectionListView,
    CollectionDetailView,
    CreatePaymentIntentView
)

urlpatterns = [
    # The Admin URL
    path('admin/', admin.site.urls),

    # --- API URLs ---
    path('api/products/', ProductAPIView.as_view(), name='product-api-list'),
    path('api/products/all/', AllProductsAPIView.as_view(), name='all-products-api'),
    path('api/products/<int:pk>/', ProductDetailAPIView.as_view(), name='product-api-detail'),
    
    path('api/categories/', CategoryListAPIView.as_view(), name='category-api-list'),
    
    path('api/collections/', CollectionListView.as_view(), name='collection-list-api'),
    path('api/collections/<slug:slug>/', CollectionDetailView.as_view(), name='collection-detail-api'),
    
    path('api/register/', RegisterView.as_view(), name='register-api'),
    path('api/login/', CustomAuthToken.as_view(), name='login-api'),
    
    path('api/orders/', OrderListAPIView.as_view(), name='order-list-api'),
    path('api/orders/create/', OrderCreateAPIView.as_view(), name='order-create-api'),
    path('api/orders/<int:pk>/cancel/', OrderCancelAPIView.as_view(), name='order-cancel-api'),
    
    path('api/create-payment-intent/', CreatePaymentIntentView.as_view(), name='create-payment-intent'),
]

# We DO NOT need the static() helper for production when using WhiteNoise.
# The middleware handles everything.
# We also DO NOT need it for media() because Cloudinary handles all media files.