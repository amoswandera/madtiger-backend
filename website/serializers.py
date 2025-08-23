# website/serializers.py

from rest_framework import serializers
from .models import Product, Category
from .models import Product, Category, Order, OrderItem
from django.contrib.auth.models import User
from .models import Collection
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        # These are the fields that will be converted to JSON
        fields = ['id', 'name', 'price', 'description', 'image']

        # New Serializer for the User model
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')
        # This ensures the password is write-only (it won't be sent back in API responses)
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # We use create_user to ensure the password gets hashed correctly
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

        # This serializer is for the individual items within an order
class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ("product", "quantity") # Removed 'price' - it should be taken from the Product model

        
# This is the main serializer for creating an Order
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, write_only=True)

    class Meta:
        model = Order
        fields = ("id", "address", "postal_code", "city", "items", "stripe_id")

    def create(self, validated_data):
        items_data = validated_data.pop('items')

        # Create the main Order instance
        order = Order.objects.create(**validated_data)
        
        # Loop through the items data to create OrderItem instances
        for item_data in items_data:
            # Get the product instance
            product = item_data['product']
            # Create the OrderItem, taking the price from the actual product to prevent manipulation
            OrderItem.objects.create(
                order=order, 
                product=product,
                price=product.price, # Set the price from the Product model
                quantity=item_data['quantity']
            )
            
        return order

class OrderProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ("id", "name", "image")

class OrderHistoryItemSerializer(serializers.ModelSerializer):
    product = OrderProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ("price", "quantity", "product")

class OrderHistorySerializer(serializers.ModelSerializer):
    items = OrderHistoryItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ("id", "created", "address", "city", "postal_code", "items")

class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ['id', 'name', 'slug', 'description', 'image']

class CollectionDetailSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)

    class Meta:
        model = Collection
        fields = ['id', 'name', 'slug', 'description', 'products']