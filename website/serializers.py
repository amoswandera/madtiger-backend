from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Product, Category, Order, OrderItem, Collection

# --- Cleaned and Corrected Serializers ---

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


# --- THIS IS THE CRITICAL FIX FOR ALL PRODUCT IMAGES ---
class ProductSerializer(serializers.ModelSerializer):
    # We add a new, read-only field that will contain the clean URL string.
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Product
        # We add 'image_url' to the list of fields the API will send to the frontend.
        fields = ['id', 'name', 'price', 'description', 'image', 'image_url']
        # The original 'image' field is now only used for uploading, not for displaying.
        extra_kwargs = {'image': {'write_only': True}}

    def get_image_url(self, obj):
        # This method safely checks if an image exists and returns its full URL.
        if obj.image and hasattr(obj.image, 'url'):
            return obj.image.url
        # If no image exists, it sends null.
        return None
# --- END CRITICAL FIX ---


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user


# This serializer is for the individual items within an order (when creating an order)
class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ("product", "quantity")


# This is the main serializer for CREATING an Order
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, write_only=True)

    class Meta:
        model = Order
        fields = ("id", "address", "postal_code", "city", "items", "stripe_id")

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)
        for item_data in items_data:
            product = item_data['product']
            OrderItem.objects.create(
                order=order, 
                product=product,
                price=product.price,
                quantity=item_data['quantity']
            )
        return order


# This serializer provides product details for VIEWING an order's history
# It has also been updated to include the 'image_url'
class OrderProductSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ("id", "name", "image_url") # Only send the clean URL

    def get_image_url(self, obj):
        if obj.image and hasattr(obj.image, 'url'):
            return obj.image.url
        return None


# This serializer formats each item within the order history list
class OrderHistoryItemSerializer(serializers.ModelSerializer):
    product = OrderProductSerializer(read_only=True) # Uses the serializer above

    class Meta:
        model = OrderItem
        fields = ("price", "quantity", "product")


# This is the main serializer for DISPLAYING the list of past orders
class OrderHistorySerializer(serializers.ModelSerializer):
    items = OrderHistoryItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ("id", "status", "created", "address", "city", "postal_code", "items")


# This serializer lists collections on the homepage, now with a clean image_url
class CollectionSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Collection
        fields = ['id', 'name', 'slug', 'description', 'image_url']

    def get_image_url(self, obj):
        if obj.image and hasattr(obj.image, 'url'):
            return obj.image.url
        return None


class CollectionDetailSerializer(serializers.ModelSerializer):
    # Because this uses ProductSerializer, it will automatically get the new 'image_url'
    products = ProductSerializer(many=True, read_only=True)

    class Meta:
        model = Collection
        fields = ['id', 'name', 'slug', 'description', 'products']