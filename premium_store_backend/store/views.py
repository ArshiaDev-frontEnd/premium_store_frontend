from django.core.exceptions import PermissionDenied
from django.core.cache import cache
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.db import transaction
from django.utils import timezone

from django_filters.rest_framework import DjangoFilterBackend

import requests
import secrets
import string

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, DestroyModelMixin
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet, ModelViewSet, ReadOnlyModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter

from kavenegar import KavenegarAPI
from datetime import timedelta

from .filters import ServiceFilter, OrderFilter
from .models import Application, Customer, Service, Comment, Cart, CartItem, Order, OrderItem, Discount, ServiceField
from .paginations import DefaultPagination
from .permissions import IsAdminOrReadOnly, IsCommentAuthorOrAdmin
from .serializers import AddCartItemSerializer, ApplicationSerializer, CustomerSerializer, OrderCreateSerializer, OrderForAdminSerializer, ServiceSerializer, CommentSerializer, CartSerializer, CartItemSerializer, OrderSerializer, OrderItemSerializer, DiscountSerializer, UpdateCartItemSerializer, EmptySerializer, VerifySerializer
from .tasks import send_sms_task



def send_sms(phone, message):
        api = KavenegarAPI(settings.KAVENEGAR_API_KEY)
        params = {
            'sender': settings.KAVENEGAR_SENDER,
            'receptor': str(phone),
            'message': message
        }
        response = api.sms_send(params)


class ApplicationViewSet(ModelViewSet):
    serializer_class = ApplicationSerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = DefaultPagination
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        return Application.objects.select_related("top_service").all()

    def initialize_request(self, request, *args, **kwargs):
        request = super().initialize_request(request, *args, **kwargs)
        if not request.user.is_authenticated or not request.user.is_staff:
            self.http_method_names = ['get', 'head', 'options']
        else:
            self.http_method_names = ['get', 'post', 'put', 'delete', 'head', 'options']
        return request


class ServiceViewSet(ModelViewSet):
    serializer_class = ServiceSerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = DefaultPagination
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    filterset_class = ServiceFilter
    search_fields = ["name"]
    ordering_fields = ["price"]
    
    
    def get_queryset(self):
        application_pk = self.kwargs["application_pk"]
        return Service.objects.filter(application_id=application_pk).select_related('discounts').prefetch_related('required_fields')
    
    def perform_create(self, serializer):
        application = get_object_or_404(Application, pk=self.kwargs['application_pk'])
        serializer.save(application=application)
    
    def initialize_request(self, request, *args, **kwargs):
        request = super().initialize_request(request, *args, **kwargs)
        if not request.user.is_authenticated or not request.user.is_staff:
            self.http_method_names = ['get', 'head', 'options']
        else:
            self.http_method_names = ['get', 'post', 'put', 'delete', 'head', 'options']
        return request


class CommentViewSet(ModelViewSet):
    serializer_class = CommentSerializer
    pagination_class = DefaultPagination
    
    def get_queryset(self):
        application_pk = self.kwargs["application_pk"]
        service_pk = self.kwargs["service_pk"]
        return Comment.objects.select_related("author").filter(service_id=service_pk, service__application_id=application_pk).all()
    
    def perform_create(self, serializer):
        service = get_object_or_404(Service, pk=self.kwargs['service_pk'])
        serializer.save(author=self.request.user, service=service)
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsCommentAuthorOrAdmin()]


class CartViewSet(CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, GenericViewSet):
    serializer_class = CartSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Cart.objects.prefetch_related(
            Prefetch(
                'items',
                queryset=CartItem.objects.select_related('service').prefetch_related(
                    Prefetch('service__required_fields', queryset=ServiceField.objects.all()),
                    'service__discounts'
                )
            )
        )
    
    def perform_create(self, serializer):
        instance = serializer.save()
        instance = self.get_queryset().get(pk=instance.pk)
        serializer.instance = instance


class CartItemViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']
    permission_classes = [AllowAny]

    def get_queryset(self):
        cart_pk = self.kwargs["cart_pk"]
        return CartItem.objects.select_related('service__discounts').prefetch_related(
            'service__required_fields'
        ).filter(cart_id=cart_pk)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return AddCartItemSerializer
        elif self.request.method == "PATCH":
            return UpdateCartItemSerializer
        return CartItemSerializer

    def get_serializer_context(self):
        return {'cart_pk': self.kwargs['cart_pk']}


class OrderViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'head', 'options']
    pagination_class = DefaultPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = OrderFilter

    def get_permissions(self):
        if self.action == 'callback':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = Order.objects.prefetch_related(
            Prefetch(
                'items',
                queryset=OrderItem.objects.select_related('service__discounts').prefetch_related('service__required_fields')
            )
        ).select_related('customer__user')

        if self.request.user.is_staff:
            return queryset
        return queryset.filter(customer__user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        
        if self.action == 'pay':
            return EmptySerializer
        
        if self.request.user.is_staff:
            return OrderForAdminSerializer
            
        return OrderSerializer

    def get_serializer_context(self):
        return {"user": self.request.user, "request": self.request}

    def create(self, request, *args, **kwargs):
        customer = Customer.objects.get(user=request.user)

        if not customer.phone_number:
            return Response(
                {
                    "error": "phone_number_required",
                    "message": "You must enter a phone number to place an order. Please register your phone number first.",
                    "redirect_url": request.build_absolute_uri("/customers/me/")
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = OrderCreateSerializer(
            data=request.data,
            context={'user': request.user}
        )
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        order_serializer = OrderSerializer(order)
        return Response(order_serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'], url_path='pay')
    def pay(self, request, pk=None):
        order = self.get_object()
        if order.status != Order.ORDER_STATUS_UNPAID:
            return Response({'error': 'The order has already been paid for or cancelled.'}, status=status.HTTP_400_BAD_REQUEST)

        total_price = sum(item.quantity * item.price for item in order.items.all())
        amount = int(total_price * 10)

        data = {
            "merchant_id": settings.ZARINPAL_MERCHANT_ID,
            "amount": amount,
            "callback_url": settings.ZARINPAL_CALLBACK_URL.format(order_id=order.id),
            "description": f"Payment for order number {order.id} - Premium Services Store",
            "metadata": {"order_id": str(order.id), "customer_email": order.customer.user.email}
        }

        try:
            response = requests.post(settings.ZARINPAL_REQUEST_URL, json=data)
            result = response.json()
        except Exception as e:
            return Response({'error': f'Error connecting to ZarinPal{str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        if 'data' in result and result['data'].get('code') == 100:
            authority = result['data']['authority']
            order.payment_authority = authority
            order.save()
            payment_url = settings.ZARINPAL_START_PAY_URL + authority
            return Response({'payment_url': payment_url}, status=status.HTTP_200_OK)
        else:
            error_msg = result.get('errors', {}).get('message', 'Unspecified error')
            return Response({'error': error_msg}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'], url_path='callback')
    def callback(self, request, pk=None):
        order = get_object_or_404(Order, pk=pk)
        authority = request.query_params.get('Authority')
        status_param = request.query_params.get('Status')


        if status_param != 'OK' or order.payment_authority != authority:
            order.status = Order.ORDER_STATUS_CANCELED
            order.save()
            return Response({'error': 'Payment unsuccessful or canceled'}, status=status.HTTP_400_BAD_REQUEST)

        total_price = sum(item.quantity * item.price for item in order.items.all())
        amount = int(total_price * 10)

        data = {
            "merchant_id": settings.ZARINPAL_MERCHANT_ID,
            "authority": authority,
            "amount": amount
        }

        try:
            response = requests.post(settings.ZARINPAL_VERIFY_URL, json=data)
            result = response.json()
        except Exception as e:
            return Response({'error': f'Error in payment confirmation: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        with transaction.atomic():
            if 'data' in result and result['data'].get('code') in [100, 101]:
                order.status = Order.ORDER_STATUS_PAID
                order.payment_ref_id = result['data'].get('ref_id')
                order.save()
                return Response({'success': 'Payment successfully confirmed', 'ref_id': order.payment_ref_id}, status=status.HTTP_200_OK)
            else:
                error_msg = result.get('errors', {}).get('message', 'Unknown error')
                order.status = Order.ORDER_STATUS_CANCELED
                order.save()
                return Response({'error': error_msg}, status=status.HTTP_400_BAD_REQUEST)


class OrderItemsViewSet(ReadOnlyModelViewSet):
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        order_pk = self.kwargs["order_pk"]
        return OrderItem.objects.select_related('service__discounts').prefetch_related('service__required_fields').filter(order_id=order_pk)


class DiscountViewSet(ModelViewSet):
    serializer_class = DiscountSerializer
    queryset = Discount.objects.all()
    permission_classes = [IsAdminOrReadOnly]


class DiscountServicesViewSet(ModelViewSet):
    serializer_class = ServiceSerializer
    http_method_names = ["get"]
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = DefaultPagination

    def get_queryset(self):
        discount_pk = self.kwargs["discount_pk"]
        return Service.objects.filter(discounts_id=discount_pk).select_related('discounts').prefetch_related('required_fields')


class DiscountServicesCommentViewSet(ModelViewSet):
    serializer_class = CommentSerializer
    pagination_class = DefaultPagination

    def get_queryset(self):
        discount_service_pk = self.kwargs["discount_service_pk"]
        discount_pk = self.kwargs["discount_pk"]
        return Comment.objects.select_related("author").filter(service_id=discount_service_pk, service__discounts__id=discount_pk).all()

    def perform_create(self, serializer):
        service = get_object_or_404(Service, pk=self.kwargs['discount_service_pk'])
        serializer.save(author=self.request.user, service=service)

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsCommentAuthorOrAdmin()]


class CustomerViewSet(GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CustomerSerializer
    queryset = Customer.objects.all()
    pagination_class = DefaultPagination

    def get_serializer_class(self):
        if self.action == 'verify_phone':
            return VerifySerializer
        return CustomerSerializer

    def list(self, request):
        if request.user.is_staff:
            queryset = Customer.objects.select_related("user").all()
        else:
            queryset = Customer.objects.select_related("user").filter(user=request.user)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        if not request.user.is_staff:
            raise PermissionDenied("Normal users do not have permission to access this address. Use '/custommers/me/'.")

        customer = get_object_or_404(Customer.objects.select_related("user"), pk=pk)
        serializer = self.get_serializer(customer)
        return Response(serializer.data)

    @action(detail=False, methods=['GET', 'PATCH', 'PUT'], url_path='me')
    def me(self, request):
        customer = Customer.objects.select_related("user").get(user=request.user)

        if request.method == 'GET':
            serializer = self.get_serializer(customer)
            return Response(serializer.data)

        serializer = self.get_serializer(customer, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        new_phone = serializer.validated_data.get('phone_number')
        if new_phone:
            if new_phone == customer.phone_number:
                return Response(serializer.data)
            code = ''.join(secrets.choice(string.digits) for _ in range(6))
            cache.set(f'pending_phone_{request.user.id}', str(new_phone), 300)
            cache.set(f'phone_verify_{request.user.id}', code, 300)
            send_sms_task.delay(new_phone, f'Your verification code is: {code}')
            serializer.validated_data.pop('phone_number', None)
            serializer.save()
            
            return Response({
                'detail': f'Verification code sent to your new phone. Please verify it using {request.build_absolute_uri('/customers/verify-phone/')} to save the number.',
                'current_data': serializer.data
            })

        serializer.save()
        return Response(serializer.data)
    
    @action(detail=False, methods=['POST'], url_path='verify-phone')
    def verify_phone(self, request):
        serializer = VerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = serializer.validated_data['code']

        stored_code = cache.get(f'phone_verify_{request.user.id}')
        pending_phone = cache.get(f'pending_phone_{request.user.id}')
        
        if stored_code and code == stored_code and pending_phone:
            customer = Customer.objects.get(user=request.user)
            customer.phone_number = pending_phone
            customer.is_phone_verified = True
            customer.save()
            cache.delete(f'phone_verify_{request.user.id}')
            cache.delete(f'pending_phone_{request.user.id}')
            customer_serializer = CustomerSerializer(customer)
            return Response({'detail': 'Phone number verified and saved successfully.', 'data': customer_serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid or expired code, or no pending phone number.'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['POST'], url_path='resend-otp')
    def resend_otp(self, request):
        user_id = request.user.id
        pending_phone = cache.get(f'pending_phone_{user_id}')
        if not pending_phone:
            return Response({'error': 'No pending phone number change. Please initiate a phone change first.'}, status=status.HTTP_400_BAD_REQUEST)

        last_sent_key = f'last_otp_sent_{user_id}'
        last_sent = cache.get(last_sent_key)
        if last_sent:
            time_since_last = timezone.now() - last_sent
            if time_since_last < timedelta(seconds=60):
                remaining = 60 - time_since_last.seconds
                return Response({'error': f'Please wait {remaining} seconds before retrying.', 'remaining_seconds': remaining}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        retry_count_key = f'otp_retry_count_{user_id}'
        retry_count = cache.get(retry_count_key, 0)
        if retry_count >= 5:
            return Response({'error': 'Maximum retry limit reached. Please try again later.'}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        code = str(secrets.randbelow(900000) + 100000)

        cache.set(f'phone_verify_{user_id}', code, 300)
        cache.set(last_sent_key, timezone.now(), 3600)
        cache.set(retry_count_key, retry_count + 1, 3600)

        send_sms_task.delay(pending_phone, f'Your new verification code is: {code}')

        return Response({'detail': 'Verification code resent successfully.'}, status=status.HTTP_200_OK)