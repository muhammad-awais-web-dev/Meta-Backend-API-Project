from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import MenuItem ,CartItem, Order

user = get_user_model()


class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = '__all__'

    def validate_price(self, value):
        if value < 5:
            raise serializers.ValidationError("Price must be at least 5.")
        return value

class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['id', 'user', 'menu_item', 'quantity', 'unit_price', 'price', 'created_at']
        read_only_fields = ['unit_price', 'price', 'created_at']

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("Quantity must be at least 1.")
        return value
    def create(self, validated_data):
        menu_item = validated_data['menu_item']
        quantity = validated_data['quantity']
        unit_price = menu_item.price
        price = unit_price * quantity

        cart_item = CartItem.objects.create(
            user=validated_data['user'],
            menu_item=menu_item,
            quantity=quantity,
            unit_price=unit_price,
            price=price
        )
        return cart_item
    def update(self, instance, validated_data):
        instance.quantity = validated_data.get('quantity', instance.quantity)
        instance.unit_price = instance.menu_item.price
        instance.price = instance.unit_price * instance.quantity
        instance.save()
        return instance

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'user', 'delivery_crew', 'status', 'total_price', 'created_at']
        read_only_fields = ['total_price', 'created_at']

    def validate_total_price(self, value):
        if value < 1:
            raise serializers.ValidationError("Total price must be at least 1.")
        return value
    def create(self, validated_data):
        order = Order.objects.create(
            user=validated_data['user'],
            delivery_crew=validated_data.get('delivery_crew'),
            status=validated_data.get('status', False),
            total_price=validated_data.get('total_price', 0)
        )
        return order
    def update(self, instance, validated_data):
        instance.status = validated_data.get('status', instance.status)
        instance.delivery_crew = validated_data.get('delivery_crew', instance.delivery_crew)
        instance.total_price = validated_data.get('total_price', instance.total_price)
        instance.save()
        return instance


