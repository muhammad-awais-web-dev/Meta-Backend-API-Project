from django.urls import path, include
from . import views

urlpatterns = [
    # Admin endpoints
    path('groups/manager/users/', views.AssignUserToManagerView.as_view(), name='assign-manager'),
    path('groups/manager/', views.ManagerGroupAccessView.as_view(), name='manager-group-access'),
    
    # Category endpoints
    path('categories/', views.CategoryListCreateView.as_view(), name='category-list-create'),
    
    # Menu item endpoints
    path('menu-items/', views.MenuItemListCreateView.as_view(), name='menu-item-list-create'),
    path('menu-items/<int:pk>/', views.MenuItemRetrieveUpdateDestroyView.as_view(), name='menu-item-detail'),
    path('menu-items/<int:pk>/item-of-day/', views.UpdateItemOfDayView.as_view(), name='update-item-of-day'),
    
    # User management endpoints
    path('groups/delivery-crew/users/', views.AssignDeliveryCrewView.as_view(), name='assign-delivery-crew'),
    
    # Cart endpoints
    path('cart/menu-items/', views.CartItemListCreateView.as_view(), name='cart-item-list-create'),
    path('cart/menu-items/<int:pk>/', views.CartItemRetrieveUpdateDestroyView.as_view(), name='cart-item-detail'),
    
    # Order endpoints
    path('orders/', views.OrderListCreateView.as_view(), name='order-list-create'),
    path('orders/<int:pk>/', views.OrderRetrieveUpdateDestroyView.as_view(), name='order-detail'),
    path('orders/<int:pk>/assign-delivery/', views.AssignOrderToDeliveryCrewView.as_view(), name='assign-order-delivery'),
    path('orders/<int:pk>/delivered/', views.MarkOrderDeliveredView.as_view(), name='mark-order-delivered'),
]