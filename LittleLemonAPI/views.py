from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from django.shortcuts import render, get_object_or_404
from rest_framework import generics, filters
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.models import User, Group
from django.db.models import Sum
from .models import MenuItem, CartItem, Order, OrderItem, Category
from .serializers import (
    MenuItemSerializer, CartItemSerializer, OrderSerializer, 
    OrderItemSerializer, CategorySerializer, UserSerializer, GroupSerializer
)

# ======= ADMIN VIEWS =======
class AssignUserToManagerView(generics.CreateAPIView):
    """Admin can assign users to manager group"""
    permission_classes = [IsAdminUser]
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        try:
            user = User.objects.get(username=username)
            manager_group, created = Group.objects.get_or_create(name='Manager')
            user.groups.add(manager_group)
            return Response({'message': f'User {username} assigned to Manager group'})
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


class ManagerGroupAccessView(generics.ListAPIView):
    """Admin can access manager group with admin token"""
    permission_classes = [IsAdminUser]
    serializer_class = UserSerializer

    def get_queryset(self):
        manager_group, created = Group.objects.get_or_create(name='Manager')
        return manager_group.user_set.all()


# ======= CATEGORY VIEWS =======
class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAdminUser()]


# ======= MENU ITEM VIEWS =======
class MenuItemListCreateView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['category', 'featured']
    ordering_fields = ['price', 'name']
    search_fields = ['name', 'description']
    
    def get_permissions(self):
        """Customers can browse, Admin can add"""
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAdminUser()]

    def get_throttles(self):
        if self.request.user.is_authenticated:
            return [UserRateThrottle()]
        else:
            return [AnonRateThrottle()]


class MenuItemRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def perform_update(self, serializer):
        # Only managers can update items
        if self.request.user.groups.filter(name='Manager').exists():
            serializer.save()
        else:
            raise PermissionError('Only managers can update menu items')

    def perform_destroy(self, instance):
        # Only managers can delete items
        if self.request.user.groups.filter(name='Manager').exists():
            instance.delete()
        else:
            raise PermissionError('Only managers can delete menu items')


class UpdateItemOfDayView(generics.UpdateAPIView):
    """Managers can update item of the day"""
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name='Manager').exists():
            return Response({'error': 'Only managers can update item of the day'}, 
                           status=status.HTTP_403_FORBIDDEN)
        
        try:
            # Remove current featured items
            MenuItem.objects.filter(featured=True).update(featured=False)
            # Set new featured item
            menu_item = self.get_object()
            menu_item.featured = True
            menu_item.save()
            return Response({'message': f'{menu_item.name} is now the item of the day'})
        except MenuItem.DoesNotExist:
            return Response({'error': 'Menu item not found'}, status=status.HTTP_404_NOT_FOUND)


# ======= USER MANAGEMENT VIEWS =======
class AssignDeliveryCrewView(generics.CreateAPIView):
    """Managers can assign users to delivery crew"""
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        if not request.user.groups.filter(name='Manager').exists():
            return Response({'error': 'Only managers can assign delivery crew'}, 
                           status=status.HTTP_403_FORBIDDEN)
        
        username = request.data.get('username')
        try:
            user = User.objects.get(username=username)
            delivery_group, created = Group.objects.get_or_create(name='Delivery crew')
            user.groups.add(delivery_group)
            return Response({'message': f'User {username} assigned to Delivery crew'})
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


# ======= CART VIEWS =======
class CartItemListCreateView(generics.ListCreateAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CartItemRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user)


# ======= ORDER VIEWS =======
class OrderListCreateView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status']
    ordering_fields = ['created_at', 'total_price']
    
    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Manager').exists():
            return Order.objects.all()
        elif user.groups.filter(name='Delivery crew').exists():
            return Order.objects.filter(delivery_crew=user)
        else:
            return Order.objects.filter(user=user)

    def perform_create(self, serializer):
        # Create order from cart items
        cart_items = CartItem.objects.filter(user=self.request.user)
        if not cart_items.exists():
            return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)
        
        total_price = cart_items.aggregate(total=Sum('price'))['total']
        order = serializer.save(user=self.request.user, total_price=total_price)
        
        # Create order items from cart items
        for cart_item in cart_items:
            OrderItem.objects.create(
                order=order,
                menu_item=cart_item.menu_item,
                quantity=cart_item.quantity,
                unit_price=cart_item.unit_price,
                price=cart_item.price
            )
        
        # Clear cart after order
        cart_items.delete()


class OrderRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Manager').exists():
            return Order.objects.all()
        elif user.groups.filter(name='Delivery crew').exists():
            return Order.objects.filter(delivery_crew=user)
        else:
            return Order.objects.filter(user=user)

    def perform_update(self, serializer):
        user = self.request.user
        # Delivery crew can only update status
        if user.groups.filter(name='Delivery crew').exists():
            # Only allow status updates
            if 'status' in serializer.validated_data and len(serializer.validated_data) == 1:
                serializer.save()
            else:
                return Response({'error': 'Delivery crew can only update order status'}, 
                              status=status.HTTP_403_FORBIDDEN)
        # Managers can assign delivery crew
        elif user.groups.filter(name='Manager').exists():
            serializer.save()
        else:
            return Response({'error': 'Customers cannot update orders'}, 
                          status=status.HTTP_403_FORBIDDEN)


class AssignOrderToDeliveryCrewView(generics.UpdateAPIView):
    """Managers can assign orders to delivery crew"""
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name='Manager').exists():
            return Response({'error': 'Only managers can assign orders'}, 
                           status=status.HTTP_403_FORBIDDEN)
        
        delivery_crew_id = request.data.get('delivery_crew_id')
        try:
            order = self.get_object()
            delivery_crew = User.objects.get(id=delivery_crew_id)
            
            if not delivery_crew.groups.filter(name='Delivery crew').exists():
                return Response({'error': 'User is not in delivery crew'}, 
                               status=status.HTTP_400_BAD_REQUEST)
            
            order.delivery_crew = delivery_crew
            order.save()
            return Response({'message': f'Order assigned to {delivery_crew.username}'})
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


class MarkOrderDeliveredView(generics.UpdateAPIView):
    """Delivery crew can mark order as delivered"""
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(delivery_crew=self.request.user)

    def patch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name='Delivery crew').exists():
            return Response({'error': 'Only delivery crew can mark orders as delivered'}, 
                           status=status.HTTP_403_FORBIDDEN)
        
        try:
            order = self.get_object()
            order.status = True  # Mark as delivered
            order.save()
            return Response({'message': 'Order marked as delivered'})
        except Order.DoesNotExist:
            return Response({'error': 'Order not found or not assigned to you'}, 
                           status=status.HTTP_404_NOT_FOUND)
