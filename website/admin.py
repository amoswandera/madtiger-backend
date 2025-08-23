# website/admin.py (Final Enhanced Version with Order Item Images)

from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product, Order, OrderItem, Collection

# --- Category Admin ---
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

# --- Product Admin ---
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['image_tag', 'name', 'slug', 'price', 'available']
    list_editable = ['price', 'available']
    list_filter = ['category', 'available']
    prepopulated_fields = {'slug': ('name',)}

    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 60px; max-width: 60px;" />'.format(obj.image.url))
        return "No Image"
    
    image_tag.short_description = 'Image'

# --- Collection Admin ---
@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'gender_category', 'is_active']
    list_filter = ['is_active', 'gender_category']
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ('products',)

# --- Order Admin (This is where we make the change) ---

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']
    
    # --- THIS IS THE NEW FEATURE ---
    # 1. Add the new 'image_tag' to the readonly_fields
    readonly_fields = ('price', 'image_tag',)
    # 2. Add 'image_tag' to the list of fields to display
    fields = ('product', 'image_tag', 'price', 'quantity')
    # --- END NEW FEATURE ---
    
    extra = 0

    def image_tag(self, obj):
        """
        Custom method to display the image of the product associated with this order item.
        """
        if obj.product.image:
            return format_html('<img src="{}" style="max-height: 60px; max-width: 60px;" />'.format(obj.product.image.url))
        return "No Image"

    image_tag.short_description = 'Product Image'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'status', 'paid', 'created']
    list_filter = ['status', 'paid', 'created']
    search_fields = ['user__username', 'id']
    inlines = [OrderItemInline]
    list_editable = ['status']