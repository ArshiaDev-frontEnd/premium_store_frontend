from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import Customer, Application, Discount, Service, Comment, Cart, CartItem, Order, OrderItem, ServiceField


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ["user", "phone_number"]


class ServiceInline(admin.TabularInline):
    model = Service
    fields = ["name", "application", "slug", "description", "price", "discounts"]
    extra = 1


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ["title", "short_description", "top_service"]
    inlines = [ServiceInline]
    readonly_fields = ("image_preview",)

    def image_preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="100" height="100" />')
        return "No Image"
    image_preview.short_description = "Image Preview"


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ["name", "discount_percent"]


class CommentsInline(admin.TabularInline):
    model = Comment
    fields = ["author", "service", "body", "status"]
    extra = 1

@admin.register(ServiceField)
class ServiceFieldAdmin(admin.ModelAdmin):
    list_display = ["service", "field_name", "field_type", "is_required", "label"]
    readonly_fields = ("is_required",)


class ServiceFieldInline(admin.TabularInline):
    model = ServiceField
    extra = 1


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ["name", "application", "short_description", "price", "datetime_created", "discounts", "image"]
    inlines = [CommentsInline, ServiceFieldInline]
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("datetime_created", "image_preview")

    def image_preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="100" height="100" />')
        return "No Image"
    image_preview.short_description = "Image Preview"


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ["author", "service", "short_body", "status", "datetime_created"]


class CartItemInline(admin.TabularInline):
    model = CartItem
    fields = ["cart", "service"]
    extra = 1


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ["id", "datetime_created"]
    inlines = [CartItemInline]


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ["cart", "service"]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    fields = ["order", "service", "price"]
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "customer", "datetime_created", "status"]
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ["formatted_order", "service", "quantity", "price", "extra_data_preview"]

    def extra_data_preview(self, obj):
        if not obj.extra_data:
            return "-"
        items = []
        for k, v in obj.extra_data.items():
            field = ServiceField.objects.filter(service=obj.service, field_name=k).first()
            label = field.label if field and field.label else k
            items.append(f"{label}: {v}")
        return mark_safe("<br>".join(items))
    extra_data_preview.short_description = "more info"

    def formatted_order(self, obj):
        order = obj.order
        customer_username = obj.order.customer.user.username
        return f"Order (ID = {order.id} , Customer = {customer_username})"
    formatted_order.short_description = "Order"