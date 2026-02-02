from rest_framework_nested import routers

from . import views


router = routers.DefaultRouter()
router.register("applications", views.ApplicationViewSet, basename="application")
router.register("carts", views.CartViewSet, basename="cart")
router.register("orders", views.OrderViewSet, basename="order")
router.register("discounts", views.DiscountViewSet, basename="discount")
router.register("customers", views.CustomerViewSet, basename="customer")


services_router = routers.NestedDefaultRouter(router, "applications", lookup="application")
services_router.register("services", views.ServiceViewSet, basename="application-service")

cartitem_router = routers.NestedDefaultRouter(router, "carts", lookup="cart")
cartitem_router.register("items", views.CartItemViewSet, basename="cart-item")

orderitem_router = routers.NestedDefaultRouter(router, "orders", lookup="order")
orderitem_router.register("items", views.OrderItemsViewSet, basename="order-item")

discount_services_router = routers.NestedDefaultRouter(router, "discounts", lookup="discount")
discount_services_router.register("services", views.DiscountServicesViewSet, basename="discount-service")

discount_services_comment_router = routers.NestedDefaultRouter(discount_services_router, "services", lookup="discount_service")
discount_services_comment_router.register("comments", views.DiscountServicesCommentViewSet, basename="discount-service-comment")

comment_router = routers.NestedDefaultRouter(services_router, "services", lookup="service")
comment_router.register("comments", views.CommentViewSet, basename="service-comment")


urlpatterns = router.urls + services_router.urls + comment_router.urls + cartitem_router.urls + orderitem_router.urls + discount_services_router.urls + discount_services_comment_router.urls