from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.template.defaultfilters import truncatechars

from decimal import Decimal

from phonenumber_field.modelfields import PhoneNumberField

from uuid import uuid4



class Customer(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    phone_number = PhoneNumberField(
        region = "IR",
        unique=True,
        blank=True,
        null=True,
        verbose_name="Phone number",
        help_text="Iranian format phone number(example: 09123456789)",
    )
    is_phone_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username


class Application(models.Model):
    title = models.CharField(max_length=250)
    description = models.TextField()
    top_service = models.ForeignKey('Service', null=True, blank=True, on_delete=models.SET_NULL, related_name='applications')
    image = models.ImageField(upload_to='applications/images/', null=True, blank=True)

    def __str__(self):
        return self.title
    
    @property
    def short_description(self):
        return truncatechars(self.description, 100)


class Discount(models.Model):
    discount_percent = models.DecimalField(
        max_digits=5, decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Enter the discount percentage"
    )
    name = models.CharField(max_length=250)

    def __str__(self):
        return self.name


class Service(models.Model):
    name = models.CharField(max_length=250)
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='services')
    image = models.ImageField(upload_to='services/images/', null=True, blank=True)
    slug = models.SlugField()
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=0)
    datetime_created = models.DateTimeField(auto_now_add=True)
    datetime_modified = models.DateTimeField(auto_now=True)
    discounts = models.ForeignKey(Discount, null=True, blank=True, on_delete=models.SET_NULL)

    def get_discounted_price(self):
        if self.discounts:
            discount_factor = Decimal(1) - (self.discounts.discount_percent / Decimal(100))
            return self.price * discount_factor
        return self.price

    def __str__(self):
        return self.name
    
    def get_required_fields(self):
        return self.required_fields.filter(is_required=True).values('field_name', 'field_type', 'label')
    
    @property
    def short_description(self):
        return truncatechars(self.description, 100)


class Comment(models.Model):
    COMMENT_STATUS_WAITING = 'w'
    COMMENT_STATUS_APPROVED = 'a'
    COMMENT_STATUS_NOT_APPROVED = 'na'
    COMMENT_STATUS = [
        (COMMENT_STATUS_WAITING, 'Waiting'),
        (COMMENT_STATUS_APPROVED, 'Approved'),
        (COMMENT_STATUS_NOT_APPROVED, 'Not Approved'),
    ]

    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments")
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="comments")
    body = models.TextField()
    status = models.CharField(max_length=2, choices=COMMENT_STATUS, default=COMMENT_STATUS_WAITING)
    datetime_created = models.DateTimeField(auto_now_add=True)
    datetime_modified = models.DateTimeField(auto_now=True)

    @property
    def short_body(self):
        return truncatechars(self.body, 75)


class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    datetime_created = models.DateTimeField(auto_now_add=True)

    def get_total_price(self):
        return sum(item.get_item_total_price() for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(default=1, validators=[MinValueValidator(1)])
    extra_data = models.JSONField(default=dict, blank=True, null=True)

    def get_item_total_price(self):
        return self.quantity * self.service.get_discounted_price()
    
    class Meta:
        unique_together = [['cart', 'service', 'extra_data']]


class Order(models.Model):
    ORDER_STATUS_PAID = 'p'
    ORDER_STATUS_UNPAID = 'u'
    ORDER_STATUS_CANCELED = 'c'
    ORDER_STATUS = [
        (ORDER_STATUS_PAID,'Paid'),
        (ORDER_STATUS_UNPAID,'Unpaid'),
        (ORDER_STATUS_CANCELED,'Canceled'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    datetime_created = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=1, choices=ORDER_STATUS, default=ORDER_STATUS_UNPAID)
    payment_authority = models.CharField(max_length=100, blank=True, null=True)
    payment_ref_id = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Order (ID = {self.id} , Customer = {self.customer.user.username})"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name="items")
    service = models.ForeignKey(Service, on_delete=models.PROTECT)
    price = models.DecimalField(max_digits=10, decimal_places=0)
    quantity = models.PositiveSmallIntegerField(default=1)
    extra_data = models.JSONField(default=dict, blank=True, null=True)

    def __str__(self):
        return f"{self.service.name} - {self.order.customer}"


class ServiceField(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='required_fields')
    field_name = models.CharField(max_length=100)
    field_type = models.CharField(max_length=50, choices=[('text', 'Text'), ('password', 'Password'), ('email', 'Email'), ('username', 'Username')])
    is_required = models.BooleanField(default=True)
    label = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.service.name} - {self.field_name}"