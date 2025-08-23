# website/views.py

from django.shortcuts import render
from .models import Category, Product
from django.utils import timezone
from datetime import timedelta

def product_list(request, category_slug=None):
    # We start by getting all available products
    products = Product.objects.filter(available=True)

    # We'll also get all categories to display them later if we want
    categories = Category.objects.all()

    # This context dictionary is what sends the data to the HTML template
    context = {
        'categories': categories,
        'products': products
    }
    return render(request, 'website/product_list.html', context)
  
from rest_framework import generics
from .models import Product, Category
from .serializers import ProductSerializer
from .serializers import ProductSerializer, CategorySerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from .serializers import UserSerializer 
from rest_framework import generics, permissions
from .models import Product, Category, Order
from .serializers import OrderHistorySerializer
import stripe
from django.conf import settings
from rest_framework.views import APIView
from .models import Collection
from .serializers import CollectionSerializer, CollectionDetailSerializer
from .serializers import ( # <-- Best practice to group imports
    ProductSerializer, 
    CategorySerializer, 
    UserSerializer, 
    OrderSerializer 
)

class CategoryListAPIView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = None

# This view will provide a read-only list of all products
class ProductAPIView(generics.ListAPIView):
    queryset = Product.objects.filter(available=True)
    serializer_class = ProductSerializer
    filterset_fields = ['category']

# This view is for retrieving a SINGLE product by its ID (pk or primary key)
class ProductDetailAPIView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
 # New View for User Registration
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

# We are extending the default login view to return the user's ID and email along with the token
class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email
        })

class OrderCreateAPIView(generics.CreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated] # Ensures only logged-in users can create an order

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(
            user=user,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            paid=True
        )

class OrderListAPIView(generics.ListAPIView):
    serializer_class = OrderHistorySerializer
    permission_classes = [permissions.IsAuthenticated] 

    def get_queryset(self):
        """
        This view should return a list of all the orders
        for the currently authenticated user.
        """
        user = self.request.user
        return Order.objects.filter(user=user).order_by('-created') 

class CreatePaymentIntentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        
        stripe.api_key = settings.STRIPE_SECRET_KEY
        
        # The frontend will send a list of items
        cart_items = request.data.get('items', [])

        if not cart_items:
            return Response({"error": "No items in cart"}, status=status.HTTP_400_BAD_REQUEST)
        total_amount = 0
        for item in cart_items:
            try:
                product = Product.objects.get(id=item.get('id'))
                total_amount += product.price * item.get('quantity')
            except Product.DoesNotExist:
                return Response({"error": f"Product with id {item.get('id')} not found."}, status=status.HTTP_404_NOT_FOUND)
        
        # The amount must be in the smallest currency unit (e.g., cents for USD)
        total_amount_in_cents = int(total_amount * 100)

        try:
            # Create a PaymentIntent with the order amount and currency
            intent = stripe.PaymentIntent.create(
                amount=total_amount_in_cents,
                currency='usd', # Change to your currency
                automatic_payment_methods={
                    'enabled': True,
                },
            )
            
            # Send the client secret back to the client
            return Response({
                'clientSecret': intent.client_secret
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)

class AllProductsAPIView(generics.ListAPIView):
    queryset = Product.objects.filter(available=True)
    serializer_class = ProductSerializer
    pagination_class = None

class CollectionListView(generics.ListAPIView):
    queryset = Collection.objects.filter(is_active=True)
    serializer_class = CollectionSerializer
    pagination_class = None
    filterset_fields = ['gender_category']

class CollectionDetailView(generics.RetrieveAPIView):
    queryset = Collection.objects.filter(is_active=True)
    serializer_class = CollectionDetailSerializer
    lookup_field = 'slug'

class OrderCancelAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk, *args, **kwargs):
        try:
            order = Order.objects.get(pk=pk, user=request.user)
        except Order.DoesNotExist:
            return Response({"error": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

        if order.status != 'processing':
            return Response({"error": "This order can no longer be cancelled."}, status=status.HTTP_400_BAD_REQUEST)

        time_since_creation = timezone.now() - order.created
        if time_since_creation > timedelta(hours=12):
            return Response({"error": "Cancellation window has passed (12 hours)."}, status=status.HTTP_400_BAD_REQUEST)
        
        order.status = 'cancelled'
        order.save()

        # --- TODO: Here you would also add logic to refund the payment via Stripe ---

        return Response({"success": "Order has been cancelled."}, status=status.HTTP_200_OK)