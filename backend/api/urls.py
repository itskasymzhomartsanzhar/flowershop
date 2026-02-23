from .models import Users, Product, Category, Orders
from django.urls import path, include
from rest_framework.routers import DefaultRouter # type: ignore

from .views import UsersViewSet, ProductViewSet, CategoryViewSet, OrdersViewSet, PosterViewSet, FavoritesViewSet, ReviewViewSet, yookassa_webhook


router = DefaultRouter()
router.register('users', UsersViewSet)
router.register('product', ProductViewSet)
router.register('category', CategoryViewSet)
router.register('orders', OrdersViewSet)
router.register('poster', PosterViewSet)
router.register(r'favorites', FavoritesViewSet, basename='favorites')
router.register(r'reviews', ReviewViewSet, basename='reviews')


urlpatterns = [
    path('payments/yookassa-webhook/', yookassa_webhook),
    path('', include(router.urls)),
]
