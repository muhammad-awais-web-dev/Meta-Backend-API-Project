# 🍋 Little Lemon API Documentation

## 📚 Overview
This API provides a comprehensive restaurant management system with role-based access control for customers, managers, delivery crew, and administrators.

## 🔐 Authentication
- **Token Authentication**: Use `Authorization: Token <your_token>` header
- **Session Authentication**: Available for web browsing
- **Registration/Login**: Available via Djoser endpoints

## 👥 User Roles
- **Admin**: Full system access (Django superuser)
- **Manager**: Menu management, user assignments, order management
- **Delivery Crew**: View assigned orders, update delivery status
- **Customer**: Browse menu, manage cart, place orders

---

## 🔑 Authentication Endpoints (Djoser)

### User Registration
- **POST** `/auth/users/`
- **Authentication**: None (Public)
- **Description**: Register a new customer account
- **Required Fields**:
  ```json
  {
    "username": "string",
    "password": "string",
    "email": "string"
  }
  ```

### User Login
- **POST** `/auth/token/login/`
- **Authentication**: None (Public)
- **Description**: Login and get access token
- **Required Fields**:
  ```json
  {
    "username": "string",
    "password": "string"
  }
  ```
- **Response**:
  ```json
  {
    "auth_token": "your_token_here"
  }
  ```

### User Logout
- **POST** `/auth/token/logout/`
- **Authentication**: Token required
- **Description**: Logout and invalidate token

---

## 👨‍💼 Admin Endpoints

### Assign User to Manager Group
- **POST** `/api/groups/manager/users/`
- **Authentication**: Admin token required
- **Role**: Admin only
- **Description**: Assign users to the manager group
- **Required Fields**:
  ```json
  {
    "username": "string"
  }
  ```

### List Manager Group Users
- **GET** `/api/groups/manager/`
- **Authentication**: Admin token required
- **Role**: Admin only
- **Description**: View all users in the manager group

---

## 📋 Category Endpoints

### List/Create Categories
- **GET** `/api/categories/`
  - **Authentication**: None (Public)
  - **Description**: Browse all categories
- **POST** `/api/categories/`
  - **Authentication**: Admin token required
  - **Role**: Admin only
  - **Description**: Create new category
  - **Required Fields**:
    ```json
    {
      "slug": "string",
      "name": "string"
    }
    ```

---

## 🍽️ Menu Item Endpoints

### List/Create Menu Items
- **GET** `/api/menu-items/`
  - **Authentication**: None (Public)
  - **Description**: Browse all menu items with filtering and sorting
  - **Query Parameters**:
    - `category=<id>`: Filter by category
    - `featured=true/false`: Filter featured items
    - `ordering=price`: Sort by price (use `-price` for descending)
    - `ordering=name`: Sort by name
    - `search=<term>`: Search in name and description
    - `page=<number>`: Pagination

- **POST** `/api/menu-items/`
  - **Authentication**: Admin token required
  - **Role**: Admin only
  - **Description**: Add new menu item
  - **Required Fields**:
    ```json
    {
      "name": "string",
      "price": "decimal",
      "category": "integer (category_id)",
      "inventory": "integer",
      "featured": "boolean",
      "description": "string"
    }
    ```

### Menu Item Details
- **GET** `/api/menu-items/{id}/`
  - **Authentication**: None (Public)
  - **Description**: View menu item details

- **PUT/PATCH** `/api/menu-items/{id}/`
  - **Authentication**: Token required
  - **Role**: Manager only
  - **Description**: Update menu item

- **DELETE** `/api/menu-items/{id}/`
  - **Authentication**: Token required
  - **Role**: Manager only
  - **Description**: Delete menu item

### Set Item of the Day
- **PATCH** `/api/menu-items/{id}/item-of-day/`
- **Authentication**: Token required
- **Role**: Manager only
- **Description**: Mark menu item as "item of the day" (featured)

---

## 🚚 User Management Endpoints

### Assign Delivery Crew
- **POST** `/api/groups/delivery-crew/users/`
- **Authentication**: Token required
- **Role**: Manager only
- **Description**: Assign users to delivery crew group
- **Required Fields**:
  ```json
  {
    "username": "string"
  }
  ```

---

## 🛒 Cart Endpoints

### List/Add Cart Items
- **GET** `/api/cart/menu-items/`
  - **Authentication**: Token required
  - **Role**: Customer
  - **Description**: View current user's cart items

- **POST** `/api/cart/menu-items/`
  - **Authentication**: Token required
  - **Role**: Customer
  - **Description**: Add item to cart
  - **Required Fields**:
    ```json
    {
      "menu_item": "integer (menu_item_id)",
      "quantity": "integer"
    }
    ```

### Cart Item Details
- **GET** `/api/cart/menu-items/{id}/`
  - **Authentication**: Token required
  - **Role**: Customer (own items only)
  - **Description**: View cart item details

- **PUT/PATCH** `/api/cart/menu-items/{id}/`
  - **Authentication**: Token required
  - **Role**: Customer (own items only)
  - **Description**: Update cart item quantity

- **DELETE** `/api/cart/menu-items/{id}/`
  - **Authentication**: Token required
  - **Role**: Customer (own items only)
  - **Description**: Remove item from cart

---

## 📦 Order Endpoints

### List/Create Orders
- **GET** `/api/orders/`
  - **Authentication**: Token required
  - **Role**: All authenticated users
  - **Description**: 
    - **Customers**: See their own orders
    - **Managers**: See all orders
    - **Delivery Crew**: See assigned orders
  - **Query Parameters**:
    - `status=true/false`: Filter by delivery status
    - `ordering=created_at`: Sort by creation date
    - `ordering=total_price`: Sort by price

- **POST** `/api/orders/`
  - **Authentication**: Token required
  - **Role**: Customer only
  - **Description**: Create order from cart items (cart will be cleared)

### Order Details
- **GET** `/api/orders/{id}/`
  - **Authentication**: Token required
  - **Role**: All authenticated users
  - **Description**: View order details (role-based access)

- **PUT/PATCH** `/api/orders/{id}/`
  - **Authentication**: Token required
  - **Role**: Manager or Delivery Crew
  - **Description**:
    - **Managers**: Can update any field
    - **Delivery Crew**: Can only update status

- **DELETE** `/api/orders/{id}/`
  - **Authentication**: Token required
  - **Role**: Manager only
  - **Description**: Delete order

### Assign Order to Delivery Crew
- **PATCH** `/api/orders/{id}/assign-delivery/`
- **Authentication**: Token required
- **Role**: Manager only
- **Description**: Assign order to delivery crew member
- **Required Fields**:
  ```json
  {
    "delivery_crew_id": "integer (user_id)"
  }
  ```

### Mark Order as Delivered
- **PATCH** `/api/orders/{id}/delivered/`
- **Authentication**: Token required
- **Role**: Delivery Crew only
- **Description**: Mark order as delivered (assigned crew member only)

---

## 🔧 Additional Features

### Rate Limiting
- **Authenticated users**: 1000 requests/day
- **Anonymous users**: 100 requests/day

### Pagination
- Default page size: 10 items
- Use `page` parameter to navigate pages

### Filtering & Search
- Menu items support category filtering
- Search functionality on menu item names and descriptions
- Sorting by price and name

### Error Handling
All endpoints return appropriate HTTP status codes:
- **200**: Success
- **201**: Created
- **400**: Bad Request
- **401**: Unauthorized
- **403**: Forbidden
- **404**: Not Found
- **500**: Internal Server Error

---

## 📝 Example Usage

### 1. Register and Login
```bash
# Register
curl -X POST http://127.0.0.1:8000/auth/users/ \
  -H "Content-Type: application/json" \
  -d '{"username": "customer1", "password": "SecurePass123", "email": "customer@example.com"}'

# Login
curl -X POST http://127.0.0.1:8000/auth/token/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "customer1", "password": "SecurePass123"}'
```

### 2. Browse Menu Items
```bash
# Get all menu items
curl http://127.0.0.1:8000/api/menu-items/

# Filter by category and sort by price
curl "http://127.0.0.1:8000/api/menu-items/?category=1&ordering=price"

# Search menu items
curl "http://127.0.0.1:8000/api/menu-items/?search=pasta"
```

### 3. Add Item to Cart (requires authentication)
```bash
curl -X POST http://127.0.0.1:8000/api/cart/menu-items/ \
  -H "Authorization: Token YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"menu_item": 1, "quantity": 2}'
```

### 4. Place Order (requires authentication)
```bash
curl -X POST http://127.0.0.1:8000/api/orders/ \
  -H "Authorization: Token YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{}'
```

---

## 🔒 Security Notes

1. **Always use HTTPS in production**
2. **Keep tokens secure and rotate them regularly**
3. **Validate all user inputs**
4. **Use proper authentication for all sensitive operations**
5. **Role-based access is strictly enforced**

---

## 🚀 Getting Started

1. Create a superuser: `python manage.py createsuperuser`
2. Create user groups: Already configured (Manager, Delivery crew)
3. Add some categories and menu items via admin or API
4. Register test users and assign roles
5. Test the complete workflow!

---

*Last updated: October 1, 2025*
*API Version: 1.0*