from django.conf import settings
from django.db import transaction

from rest_framework import serializers

from .models import Application, Customer, Service, Comment, Cart, CartItem, Order, OrderItem, Discount, ServiceField


class ApplicationSerializer(serializers.ModelSerializer):
    top_service = serializers.SlugRelatedField(
        slug_field='name',
        queryset=Service.objects.all(),
        allow_null=True
    )
    image = serializers.ImageField(write_only=True, required=False, allow_null=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Application
        fields = ["id", "title", "description", "top_service", "image", "image_url"]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance:
            self.fields['top_service'].read_only = True
        elif isinstance(self.instance, Application):
            self.fields['top_service'].queryset = self.instance.services.all()
    
    def validate_top_service(self, value):
        if value and self.instance and value.application != self.instance:
            raise serializers.ValidationError("The selected premium service must belong to this application.")
        return value
    
    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            path = obj.image.url
        else:
            path = settings.STATIC_URL + 'store/images/default_application.jpg'
        if request is not None:
            return request.build_absolute_uri(path)
        else:
            base_url = 'http://127.0.0.1:8000'
            return base_url + path
    
    def update(self, instance, validated_data):
        if 'image' in validated_data and validated_data['image'] is None:
            validated_data.pop('image')
        return super().update(instance, validated_data)


class ServiceFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceField
        fields = ['field_name', 'field_type', 'is_required', 'label']


class ServiceSerializer(serializers.ModelSerializer):
    discounted_price = serializers.SerializerMethodField()
    image = serializers.ImageField(write_only=True, required=False, allow_null=True)
    image_url = serializers.SerializerMethodField()
    required_fields = ServiceFieldSerializer(many=True, read_only=True)
    discounts = serializers.SlugRelatedField(
        slug_field='name',
        queryset=Discount.objects.all(),
        allow_null=True
    )

    class Meta:
        model = Service
        fields = ["id", "name", "description", "price", "discounts", "discounted_price", "image", "image_url", "required_fields"]
    
    def get_discounted_price(self, obj):
        return obj.get_discounted_price()
    
    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            path = obj.image.url
        else:
            path = settings.STATIC_URL + 'store/images/default_service.jpg'
        if request is not None:
            return request.build_absolute_uri(path)
        else:
            base_url = 'http://127.0.0.1:8000'
            return base_url + path
    
    def update(self, instance, validated_data):
        if 'image' in validated_data and validated_data['image'] is None:
            validated_data.pop('image')
        return super().update(instance, validated_data)


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField()

    class Meta:
        model = Comment
        fields = ["id", "author", "body", "datetime_created"]
        read_only_fields = ["author"]


class CartItemExtraDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['extra_data']
        extra_kwargs = {'extra_data': {'required': True}}


class AddCartItemSerializer(serializers.ModelSerializer):
    extra_data = serializers.JSONField(required=False, default=dict, allow_null=True)

    class Meta:
        model = CartItem
        fields = ["id", "service", "quantity", "extra_data"]

    def validate(self, data):
        service = data['service']
        raw_extra_data = data.get('extra_data', {})

        if data.get('extra_data') is None:
            raise serializers.ValidationError("Please enter the required information.")

        allowed_fields = {field.field_name for field in service.required_fields.all()}

        cleaned_extra_data = {k: v for k, v in raw_extra_data.items() if k in allowed_fields}

        required_fields = service.required_fields.filter(is_required=True)
        missing = []
        for field in required_fields:
            value = cleaned_extra_data.get(field.field_name)
            if not value or str(value).strip() == '':
                label = field.label or field.field_name.replace('_', ' ').title()
                missing.append(label)

        if missing:
            raise serializers.ValidationError(
                f"The required fields for the service «{service.name}» are not filled: {', '.join(missing)}"
            )

        data['extra_data'] = cleaned_extra_data
        return data

    def create(self, validated_data):
        cart_pk = self.context.get('cart_pk')
        service = validated_data.pop('service')
        quantity = validated_data.pop('quantity', 1)
        extra_data = validated_data.pop('extra_data', {})

        existing_item = CartItem.objects.filter(
            cart_id=cart_pk,
            service=service,
            extra_data=extra_data
        ).first()

        if existing_item:
            existing_item.quantity += quantity
            existing_item.save()
            return existing_item
        else:
            return CartItem.objects.create(
                cart_id=cart_pk,
                service=service,
                quantity=quantity,
                extra_data=extra_data
            )


class UpdateCartItemSerializer(serializers.ModelSerializer):
    extra_data = serializers.JSONField(required=False, default=dict, allow_null=True)

    class Meta:
        model = CartItem
        fields = ["quantity", "extra_data"]

    def validate(self, data):
        service = self.instance.service
        raw_extra_data = data.get('extra_data', self.instance.extra_data or {})

        if data.get('extra_data') is None:
            raise serializers.ValidationError("Please enter the required information.")

        allowed_fields = {field.field_name for field in service.required_fields.all()}

        cleaned_extra_data = {k: v for k, v in raw_extra_data.items() if k in allowed_fields}

        required_fields = service.required_fields.filter(is_required=True)
        missing = []
        for field in required_fields:
            value = cleaned_extra_data.get(field.field_name)
            if not value or str(value).strip() == '':
                label = field.label or field.field_name.replace('_', ' ').title()
                missing.append(label)

        if missing:
            raise serializers.ValidationError(
                f"The required fields for the service «{service.name}» are not filled: {', '.join(missing)}"
            )

        data['extra_data'] = cleaned_extra_data
        return data

    def update(self, instance, validated_data):
        instance.quantity = validated_data.get('quantity', instance.quantity)
        instance.extra_data = validated_data.get('extra_data', instance.extra_data)
        instance.save()
        return instance


class CartItemSerializer(serializers.ModelSerializer):
    service = ServiceSerializer(read_only=True)
    item_total_price = serializers.SerializerMethodField()
    extra_data = serializers.JSONField(read_only=True)

    class Meta:
        model = CartItem
        fields = ["id", "service", "quantity", "item_total_price", "extra_data"]

    def get_item_total_price(self, obj):
        return obj.get_item_total_price()


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_cart_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ["id", "datetime_created", "items", "total_cart_price"]
        read_only_fields = ["id"]

    def get_total_cart_price(self, obj):
        return obj.get_total_price()


class OrderItemSerializer(serializers.ModelSerializer):
    service = ServiceSerializer(read_only=True)
    item_total_price = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ["id", "service", "quantity", "price", "item_total_price", "extra_data"]

    def get_item_total_price(self, obj):
        return obj.quantity * obj.price


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    total_order_price = serializers.SerializerMethodField()
    payment_authority = serializers.CharField(read_only=True)
    payment_ref_id = serializers.CharField(read_only=True)
    customer = serializers.StringRelatedField()

    class Meta:
        model = Order
        fields = ["id", "customer", "datetime_created", "status", "items", "total_order_price", "payment_authority", "payment_ref_id"]
        read_only_fields = ["id", "datetime_created", "customer", "items", "total_order_price", "payment_authority", "payment_ref_id", "status"]

    def get_total_order_price(self, obj):
        return sum(item.quantity * item.price for item in obj.items.all())


class OrderForAdminSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    customer = serializers.StringRelatedField()
    payment_authority = serializers.CharField(read_only=True)
    payment_ref_id = serializers.CharField(read_only=True)

    class Meta:
        model = Order
        fields = ["id", "customer", "datetime_created", "status", "items", "payment_authority", "payment_ref_id"]


class OrderCreateSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()

    def validate(self, data):
        cart_id = data['cart_id']

        try:
            cart = Cart.objects.prefetch_related('items__service__required_fields').get(pk=cart_id)
        except Cart.DoesNotExist:
            raise serializers.ValidationError("There is no shopping cart with this ID. It may have expired.")

        if not cart.items.exists():
            raise serializers.ValidationError("The shopping cart is empty. Please add a service first.")

        missing_errors = []

        for item in cart.items.all():
            service = item.service
            extra_data = item.extra_data or {}
            required_fields = service.required_fields.filter(is_required=True)
            missing = []
            for field in required_fields:
                value = extra_data.get(field.field_name)
                if not value or str(value).strip() == '':
                    label = field.label or field.field_name.replace('_', ' ').title()
                    missing.append(label)

            if missing:
                missing_errors.append(
                    f"Service «{service.name}»: {', '.join(missing)}"
                )

        if missing_errors:
            error_message = "The following mandatory fields in the shopping cart are not filled:\n" + "\n".join(missing_errors)
            error_message += "\n\nPlease return to the shopping cart and enter the necessary information."
            raise serializers.ValidationError(error_message)

        return data

    def save(self, **kwargs):
        with transaction.atomic():
            cart_id = self.validated_data["cart_id"]
            user = self.context["user"]
            customer = Customer.objects.get(user=user)

            order = Order(customer=customer, status=Order.ORDER_STATUS_UNPAID)
            order.save()

            cart_items = CartItem.objects.select_related("service").filter(cart_id=cart_id)

            order_items = []
            for item in cart_items:
                discounted_price = item.service.get_discounted_price()
                order_item = OrderItem(
                    order=order,
                    service=item.service,
                    quantity=item.quantity,
                    price=discounted_price,
                    extra_data=item.extra_data or {}
                )
                order_items.append(order_item)

            OrderItem.objects.bulk_create(order_items)

            Cart.objects.filter(pk=cart_id).delete()

            return order


class DiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discount
        fields = ["id", "name", "discount_percent"]


class CustomerSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Customer
        fields = ['id', 'username', 'email', 'phone_number', 'is_phone_verified']
        read_only_fields = ['id', 'username', 'email', 'is_phone_verified']


class EmptySerializer(serializers.Serializer):
    pass


class VerifySerializer(serializers.Serializer):
    code = serializers.CharField(max_length=6, min_length=6)