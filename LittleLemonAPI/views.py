from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from django.shortcuts import render, get_object_or_404
from rest_framework import generics
from .models import MenuItem, CartItem, Order
from .serializers import MenuItemSerializer, CartItemSerializer, OrderSerializer

class MenuItemListCreateView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    def get_permissions(self):
        """
        Allow anyone to view menu items (GET), but require Manager role for creating (POST)
        """
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_throttles(self):
        if self.request.user.is_authenticated:
            return [UserRateThrottle()]
        else:
            return [AnonRateThrottle()]

    def post(self, request):
        if request.user.groups.filter(name='Manager').exists():
            return super().post(request)
        else:
            return Response({'detail': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)



class MenuItemRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    def put(self, request):
        if request.user.groups.filter(name='Manager').exists():
            return super().put(request)
        else:
            return Response({'detail': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)

    def patch(self, request):
        if request.user.groups.filter(name='Manager').exists():
            return super().patch(request)
        else:
            return Response({'detail': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)

    def delete(self, request):
        if request.user.groups.filter(name='Manager').exists():
            return super().delete(request)
        else:
            return Response({'detail': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)


class CartItemListCreateView(generics.ListCreateAPIView):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
