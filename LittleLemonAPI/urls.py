from django.urls import path, include
from . import views

urlpatterns = [
    path('menu-items/', views.MenuItemListCreateView.as_view(), name='menu-item-list-create'),
    path('menu-items/<int:pk>/', views.MenuItemRetrieveUpdateDestroyView.as_view(), name='menu-item-detail'),
    path('cart-items/', views.CartItemListCreateView.as_view(), name='cart-item-list-create'),
]