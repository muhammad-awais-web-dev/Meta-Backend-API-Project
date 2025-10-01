# 🚀 Little Lemon API – Complete Implementation Guide

## 📌 Goal
In this project, you will build a **fully functioning API** for the **Little Lemon Restaurant** using **Django REST Framework (DRF)**.

By the end, you will be able to:
- ✅ Create a RESTful API with proper authentication and authorization
- ✅ Implement role-based access control (Manager, Delivery Crew, Customer)
- ✅ Build endpoints for menu items, cart management, and order processing
- ✅ Apply filtering, pagination, sorting, and throttling
- ✅ Use Django's user groups for permission management

---

## 📖 Introduction
The Little Lemon Restaurant needs a comprehensive API system to manage their operations.  
You are tasked with **building the backend API** that will allow:

- **Customers** to browse menu items, manage their cart, and place orders
- **Managers** to manage menu items, assign delivery crew, and oversee all orders
- **Delivery Crew** to view and update their assigned orders

This guide provides step-by-step instructions to implement all required functionality.

---

## 🛠️ Setup Instructions

1. Clone or open the project folder containing the Django project.
2. Navigate to the directory containing the `Pipfile`.
3. Initialize and install dependencies:

```bash
pipenv shell
pipenv install
```

You should now see `(Meta-Backend-API-Project)` or similar in your terminal prompt.

---

## 📂 File Modifications Required
You will mainly work with:

- `LittleLemonAPI/models.py` – Database models
- `LittleLemonAPI/serializers.py` – Data serialization
- `LittleLemonAPI/views.py` – API endpoints and business logic
- `LittleLemonAPI/urls.py` – URL routing
- `littlelemon/settings.py` – Project configuration
- `littlelemon/urls.py` – Main URL configuration

---

## 📑 Steps

### **Step 1 – Create Database Models**
In **LittleLemonAPI/models.py**:

```python
from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    slug = models.SlugField()
    title = models.CharField(max_length=255, db_index=True)
    
    def __str__(self):
        return self.title

class MenuItem(models.Model):
    title = models.CharField(max_length=255, db_index=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, db_index=True)
    featured = models.BooleanField(db_index=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    
    def __str__(self):
        return self.title

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    menuitem = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.SmallIntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    
    class Meta:
        unique_together = ('menuitem', 'user')

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    delivery_crew = models.ForeignKey(
        User, on_delete=models.SET_NULL, 
        related_name="delivery_crew", 
        null=True
    )
    status = models.BooleanField(db_index=True, default=0)
    total = models.DecimalField(max_digits=6, decimal_places=2)
    date = models.DateField(db_index=True)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    menuitem = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.SmallIntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    
    class Meta:
        unique_together = ('order', 'menuitem')
```

---

### **Step 2 – Create Serializers**
Create **LittleLemonAPI/serializers.py**:

```python
from rest_framework import serializers
from .models import Category, MenuItem, Cart, Order, OrderItem
from django.contrib.auth.models import User

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'slug', 'title']

class MenuItemSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price', 'featured', 'category', 'category_id']

class CartSerializer(serializers.ModelSerializer):
    menuitem = MenuItemSerializer(read_only=True)
    menuitem_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Cart
        fields = ['id', 'user', 'menuitem', 'menuitem_id', 'quantity', 'unit_price', 'price']
        read_only_fields = ['user', 'unit_price', 'price']

class OrderItemSerializer(serializers.ModelSerializer):
    menuitem = MenuItemSerializer(read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'menuitem', 'quantity', 'unit_price', 'price']

class OrderSerializer(serializers.ModelSerializer):
    orderitem_set = OrderItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'user', 'delivery_crew', 'status', 'total', 'date', 'orderitem_set']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']
```

---

### **Step 3 – Configure Django Settings**
In **littlelemon/settings.py**, add to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'djoser',
    'django_filters',
    'LittleLemonAPI',
]
```

Add REST Framework configuration at the end of the file:

```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.OrderingFilter',
        'rest_framework.filters.SearchFilter',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',
        'user': '1000/day'
    }
}

DJOSER = {
    'USER_ID_FIELD': 'username',
}
```

---

### **Step 4 – Register Models in Admin**
In **LittleLemonAPI/admin.py**:

```python
from django.contrib import admin
from .models import Category, MenuItem, Cart, Order, OrderItem

admin.site.register(Category)
admin.site.register(MenuItem)
admin.site.register(Cart)
admin.site.register(Order)
admin.site.register(OrderItem)
```

---

### **Step 5 – Create API Views**
Create **LittleLemonAPI/views.py**:

```python
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404
from .models import Category, MenuItem, Cart, Order, OrderItem
from .serializers import (
    CategorySerializer, MenuItemSerializer, CartSerializer,
    OrderSerializer, UserSerializer
)
from datetime import date

# Menu Items Views
class MenuItemsView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    filterset_fields = ['category', 'featured']
    search_fields = ['title']
    ordering_fields = ['price', 'title']
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return []
        return [IsAdminUser()]

class SingleMenuItemView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return []
        return [IsAdminUser()]

# Manager Group Management
@api_view(['GET', 'POST'])
@permission_classes([IsAdminUser])
def managers(request):
    if request.method == 'GET':
        users = User.objects.filter(groups__name='Manager')
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
    
    if request.method == 'POST':
        username = request.data.get('username')
        if username:
            user = get_object_or_404(User, username=username)
            managers_group = Group.objects.get(name='Manager')
            managers_group.user_set.add(user)
            return Response({'message': 'User added to Manager group'}, status=status.HTTP_201_CREATED)
        return Response({'error': 'Username required'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def remove_manager(request, userId):
    user = get_object_or_404(User, pk=userId)
    managers_group = Group.objects.get(name='Manager')
    managers_group.user_set.remove(user)
    return Response({'message': 'User removed from Manager group'}, status=status.HTTP_200_OK)

# Delivery Crew Group Management
@api_view(['GET', 'POST'])
@permission_classes([IsAdminUser])
def delivery_crew(request):
    if request.method == 'GET':
        users = User.objects.filter(groups__name='Delivery Crew')
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
    
    if request.method == 'POST':
        username = request.data.get('username')
        if username:
            user = get_object_or_404(User, username=username)
            crew_group = Group.objects.get(name='Delivery Crew')
            crew_group.user_set.add(user)
            return Response({'message': 'User added to Delivery Crew group'}, status=status.HTTP_201_CREATED)
        return Response({'error': 'Username required'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def remove_delivery_crew(request, userId):
    user = get_object_or_404(User, pk=userId)
    crew_group = Group.objects.get(name='Delivery Crew')
    crew_group.user_set.remove(user)
    return Response({'message': 'User removed from Delivery Crew group'}, status=status.HTTP_200_OK)

# Cart Management
class CartView(generics.ListCreateAPIView):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        menuitem = get_object_or_404(MenuItem, pk=self.request.data.get('menuitem_id'))
        quantity = int(self.request.data.get('quantity', 1))
        unit_price = menuitem.price
        price = unit_price * quantity
        serializer.save(user=self.request.user, unit_price=unit_price, price=price)
    
    def delete(self, request):
        Cart.objects.filter(user=request.user).delete()
        return Response({'message': 'Cart cleared'}, status=status.HTTP_200_OK)

# Order Management
class OrderView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status', 'delivery_crew']
    ordering_fields = ['date', 'total']
    
    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Manager').exists():
            return Order.objects.all()
        elif user.groups.filter(name='Delivery Crew').exists():
            return Order.objects.filter(delivery_crew=user)
        return Order.objects.filter(user=user)
    
    def perform_create(self, serializer):
        cart_items = Cart.objects.filter(user=self.request.user)
        if not cart_items:
            return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)
        
        total = sum(item.price for item in cart_items)
        order = serializer.save(user=self.request.user, total=total, date=date.today())
        
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                menuitem=item.menuitem,
                quantity=item.quantity,
                unit_price=item.unit_price,
                price=item.price
            )
        
        cart_items.delete()

class SingleOrderView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Manager').exists():
            return Order.objects.all()
        elif user.groups.filter(name='Delivery Crew').exists():
            return Order.objects.filter(delivery_crew=user)
        return Order.objects.filter(user=user)
    
    def update(self, request, *args, **kwargs):
        order = self.get_object()
        
        # Managers can assign delivery crew and update status
        if request.user.groups.filter(name='Manager').exists():
            if 'delivery_crew' in request.data:
                crew_id = request.data.get('delivery_crew')
                order.delivery_crew = get_object_or_404(User, pk=crew_id)
            if 'status' in request.data:
                order.status = request.data.get('status')
            order.save()
            serializer = self.get_serializer(order)
            return Response(serializer.data)
        
        # Delivery crew can only update status
        elif request.user.groups.filter(name='Delivery Crew').exists():
            if 'status' in request.data:
                order.status = request.data.get('status')
                order.save()
                serializer = self.get_serializer(order)
                return Response(serializer.data)
            return Response({'error': 'Delivery crew can only update status'}, status=status.HTTP_403_FORBIDDEN)
        
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    def destroy(self, request, *args, **kwargs):
        if request.user.groups.filter(name='Manager').exists():
            return super().destroy(request, *args, **kwargs)
        return Response({'error': 'Only managers can delete orders'}, status=status.HTTP_403_FORBIDDEN)
```

---

### **Step 6 – Configure URL Routing**
In **LittleLemonAPI/urls.py** (create if it doesn't exist):

```python
from django.urls import path
from . import views

urlpatterns = [
    # Menu Items
    path('menu-items', views.MenuItemsView.as_view()),
    path('menu-items/<int:pk>', views.SingleMenuItemView.as_view()),
    
    # Manager Group Management
    path('groups/manager/users', views.managers),
    path('groups/manager/users/<int:userId>', views.remove_manager),
    
    # Delivery Crew Group Management
    path('groups/delivery-crew/users', views.delivery_crew),
    path('groups/delivery-crew/users/<int:userId>', views.remove_delivery_crew),
    
    # Cart Management
    path('cart/menu-items', views.CartView.as_view()),
    
    # Order Management
    path('orders', views.OrderView.as_view()),
    path('orders/<int:pk>', views.SingleOrderView.as_view()),
]
```

In **littlelemon/urls.py**, update to include:

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('LittleLemonAPI.urls')),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
```

---

### **Step 7 – Run Migrations**
Apply the database migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

---

### **Step 8 – Create Superuser**
Create an admin account:

```bash
python manage.py createsuperuser
```

Example credentials:

| Field    | Value                       |
|----------|-----------------------------|
| Username | `admin`                     |
| Email    | `admin@littlelemon.com`     |
| Password | `admin@123!`                |

---

### **Step 9 – Create User Groups**
Start the development server:

```bash
python manage.py runserver
```

Visit: [http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin)

1. Login with superuser credentials
2. Go to **Groups** → **Add Group**
3. Create two groups:
   - `Manager`
   - `Delivery Crew`

---

### **Step 10 – Create Test Users**
Inside Django Admin → Users → Add User:

Create at least 3 users for testing:

| Username    | Email                      | Password      | Group          |
|-------------|----------------------------|---------------|----------------|
| manager1    | manager@littlelemon.com    | manager@123!  | Manager        |
| crew1       | crew@littlelemon.com       | crew@123!     | Delivery Crew  |
| customer1   | customer@littlelemon.com   | customer@123! | (none)         |

After creating each user:
- Edit the user
- Scroll to **Groups** section
- Add them to appropriate group (except customer1)
- Save

---

### **Step 11 – Add Sample Categories and Menu Items**
In Django Admin:

1. Create **Categories**:
   - Appetizers (slug: appetizers)
   - Main Course (slug: main-course)
   - Desserts (slug: desserts)

2. Create **Menu Items**:

| Title              | Price  | Featured | Category     |
|--------------------|--------|----------|--------------|
| Caesar Salad       | 8.99   | Yes      | Appetizers   |
| Garlic Bread       | 5.99   | No       | Appetizers   |
| Grilled Salmon     | 18.99  | Yes      | Main Course  |
| Pasta Carbonara    | 14.99  | No       | Main Course  |
| Chocolate Cake     | 7.99   | Yes      | Desserts     |

---

### **Step 12 – Generate User Tokens**
You can generate tokens using the API:

**POST** → `http://127.0.0.1:8000/auth/token/login/`

Body (JSON):
```json
{
  "username": "customer1",
  "password": "customer@123!"
}
```

Response:
```json
{
  "auth_token": "your_token_here"
}
```

Repeat for all test users and save their tokens.

---

### **Step 13 – Test Menu Items Endpoint (GET)**
**GET** → `http://127.0.0.1:8000/api/menu-items`

No authentication required.

Response:
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Caesar Salad",
      "price": "8.99",
      "featured": true,
      "category": {
        "id": 1,
        "slug": "appetizers",
        "title": "Appetizers"
      }
    }
    // ... more items
  ]
}
```

---

### **Step 14 – Test Menu Items Filtering and Sorting**
Test filtering by category:

**GET** → `http://127.0.0.1:8000/api/menu-items?category=1`

Test sorting by price:

**GET** → `http://127.0.0.1:8000/api/menu-items?ordering=price`

Test search:

**GET** → `http://127.0.0.1:8000/api/menu-items?search=salmon`

---

### **Step 15 – Test Adding Menu Item (Manager Only)**
**POST** → `http://127.0.0.1:8000/api/menu-items`

Headers:
```
Authorization: Token <manager_token>
```

Body (JSON):
```json
{
  "title": "Chicken Tikka",
  "price": "16.99",
  "featured": true,
  "category_id": 2
}
```

Expected Response (201 Created):
```json
{
  "id": 6,
  "title": "Chicken Tikka",
  "price": "16.99",
  "featured": true,
  "category": {
    "id": 2,
    "slug": "main-course",
    "title": "Main Course"
  }
}
```

Try the same request with customer token → should return **403 Forbidden**.

---

### **Step 16 – Test Cart Management (Customer)**
**POST** → `http://127.0.0.1:8000/api/cart/menu-items`

Headers:
```
Authorization: Token <customer_token>
```

Body (JSON):
```json
{
  "menuitem_id": 3,
  "quantity": 2
}
```

Expected Response (201 Created):
```json
{
  "id": 1,
  "user": 3,
  "menuitem": {
    "id": 3,
    "title": "Grilled Salmon",
    "price": "18.99",
    "featured": true,
    "category": {...}
  },
  "quantity": 2,
  "unit_price": "18.99",
  "price": "37.98"
}
```

---

### **Step 17 – View Cart**
**GET** → `http://127.0.0.1:8000/api/cart/menu-items`

Headers:
```
Authorization: Token <customer_token>
```

Response:
```json
[
  {
    "id": 1,
    "user": 3,
    "menuitem": {...},
    "quantity": 2,
    "unit_price": "18.99",
    "price": "37.98"
  }
]
```

---

### **Step 18 – Place Order**
**POST** → `http://127.0.0.1:8000/api/orders`

Headers:
```
Authorization: Token <customer_token>
```

Body: (empty - cart items will be converted to order)

Expected Response (201 Created):
```json
{
  "id": 1,
  "user": 3,
  "delivery_crew": null,
  "status": false,
  "total": "37.98",
  "date": "2024-01-15",
  "orderitem_set": [
    {
      "id": 1,
      "menuitem": {...},
      "quantity": 2,
      "unit_price": "18.99",
      "price": "37.98"
    }
  ]
}
```

Cart should be empty after placing order.

---

### **Step 19 – View Customer Orders**
**GET** → `http://127.0.0.1:8000/api/orders`

Headers:
```
Authorization: Token <customer_token>
```

Customers see only their own orders.

---

### **Step 20 – Manager Assigns Delivery Crew**
**PATCH** → `http://127.0.0.1:8000/api/orders/1`

Headers:
```
Authorization: Token <manager_token>
```

Body (JSON):
```json
{
  "delivery_crew": 2
}
```

Expected Response (200 OK):
```json
{
  "id": 1,
  "user": 3,
  "delivery_crew": 2,
  "status": false,
  "total": "37.98",
  "date": "2024-01-15",
  "orderitem_set": [...]
}
```

---

### **Step 21 – Delivery Crew Updates Order Status**
**PATCH** → `http://127.0.0.1:8000/api/orders/1`

Headers:
```
Authorization: Token <crew_token>
```

Body (JSON):
```json
{
  "status": true
}
```

Expected Response (200 OK):
```json
{
  "id": 1,
  "user": 3,
  "delivery_crew": 2,
  "status": true,
  "total": "37.98",
  "date": "2024-01-15",
  "orderitem_set": [...]
}
```

---

### **Step 22 – Test User Group Management (Admin Only)**
**GET** → `http://127.0.0.1:8000/api/groups/manager/users`

Headers:
```
Authorization: Token <admin_token>
```

Response:
```json
[
  {
    "id": 2,
    "username": "manager1",
    "email": "manager@littlelemon.com"
  }
]
```

**POST** → `http://127.0.0.1:8000/api/groups/manager/users`

Headers:
```
Authorization: Token <admin_token>
```

Body (JSON):
```json
{
  "username": "newmanager"
}
```

---

### **Step 23 – Test Throttling**
Make multiple rapid requests to any endpoint:

After exceeding the limit, you'll receive:
```json
{
  "detail": "Request was throttled. Expected available in X seconds."
}
```

---

### **Step 24 – Test User Registration**
**POST** → `http://127.0.0.1:8000/auth/users/`

Body (JSON):
```json
{
  "username": "newcustomer",
  "email": "newcustomer@example.com",
  "password": "SecurePass123!"
}
```

Expected Response (201 Created):
```json
{
  "email": "newcustomer@example.com",
  "username": "newcustomer",
  "id": 5
}
```

---

### **Step 25 – Verify All Endpoints**
Go through the checklist:

- ✅ User registration and token generation
- ✅ Menu items browsing (all users)
- ✅ Menu items management (managers only)
- ✅ Cart management (customers only)
- ✅ Order placement (customers)
- ✅ Order viewing (role-based)
- ✅ Order management (managers)
- ✅ Delivery crew assignment (managers)
- ✅ Order status updates (delivery crew)
- ✅ User group management (admin)
- ✅ Pagination, filtering, and sorting
- ✅ Throttling for all users

---

## ✅ Conclusion
In this project, you have:

- Built a **complete RESTful API** with Django REST Framework
- Implemented **role-based access control** using Django user groups
- Created **CRUD operations** for menu items, cart, and orders
- Applied **authentication** using Token and Session authentication
- Implemented **filtering, pagination, sorting**, and **throttling**
- Used **Djoser** for user registration and authentication endpoints
- Managed **user permissions** for different roles (Manager, Delivery Crew, Customer)

Congratulations on completing the Little Lemon API project! 🎉
