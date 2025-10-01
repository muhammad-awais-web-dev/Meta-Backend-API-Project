
# Little Lemon API Project Guide

## Introduction
This guide provides an overview of the scope of the project, all necessary endpoints, and important notes for successful completion.

---

## Scope
You will build a fully functioning API project for the **Little Lemon Restaurant**.  
The API will allow users with different roles to:

- Browse, add, and edit menu items  
- Place orders  
- Browse orders  
- Assign delivery crew to orders  
- Deliver orders  

---

## Project Structure
- Create a **Django app** named `LittleLemonAPI`
- Use **pipenv** for dependency management
- Use **function- or class-based views**
- Follow proper **API naming conventions**

---

## User Groups
- **Manager**
- **Delivery Crew**
- Unassigned users = **Customers**

---

## Error Handling & Status Codes
- **200 - OK** → Successful GET, PUT, PATCH, DELETE  
- **201 - Created** → Successful POST  
- **403 - Unauthorized** → Authorization failed  
- **401 - Forbidden** → Authentication failed  
- **400 - Bad Request** → Validation failed  
- **404 - Not Found** → Resource doesn’t exist  

---

## API Endpoints

### User Registration & Token
- `POST /api/users` → Register new user  
- `GET /api/users/users/me/` → Get current user  
- `POST /token/login/` → Generate tokens  

### Menu Items
- Customers & Delivery Crew:  
  - `GET /api/menu-items` → List items  
  - `GET /api/menu-items/{id}` → Single item  
- Manager:  
  - `POST /api/menu-items` → Add item  
  - `PUT/PATCH /api/menu-items/{id}` → Update item  
  - `DELETE /api/menu-items/{id}` → Delete item  

### User Group Management
- Manager:  
  - `GET/POST /api/groups/manager/users`  
  - `DELETE /api/groups/manager/users/{userId}`  
  - `GET/POST /api/groups/delivery-crew/users`  
  - `DELETE /api/groups/delivery-crew/users/{userId}`  

### Cart Management
- Customer:  
  - `GET /api/cart/menu-items` → View cart  
  - `POST /api/cart/menu-items` → Add item  
  - `DELETE /api/cart/menu-items` → Clear cart  

### Orders
- Customer:  
  - `GET /api/orders` → View own orders  
  - `POST /api/orders` → Place new order  
  - `GET /api/orders/{id}` → Order details  
- Manager:  
  - `GET /api/orders` → View all orders  
  - `PUT/PATCH /api/orders/{id}` → Assign crew / update status  
  - `DELETE /api/orders/{id}` → Delete order  
- Delivery Crew:  
  - `GET /api/orders` → View assigned orders  
  - `PATCH /api/orders/{id}` → Update delivery status  

---

## Database Models

### Category
- `slug` (SlugField)  
- `title` (CharField, indexed, max 255)  

### MenuItem
- `title` (CharField)  
- `price` (DecimalField)  
- `featured` (BooleanField)  
- `category` (ForeignKey to Category)  

### Cart
- `user` (FK to User)  
- `menu_item` (FK to MenuItem)  
- `quantity` (IntegerField)  
- `unit_price` (DecimalField)  
- `price` (DecimalField)  

### Order
- `user` (FK to User)  
- `delivery_crew` (FK to User, related_name="delivery_crew")  
- `status` (BooleanField, default=0)  
- `total` (DecimalField)  
- `date` (DateTimeField)  

### OrderItem
- `order` (FK to Order)  
- `menu_item` (FK to MenuItem)  
- `quantity` (IntegerField)  
- `unit_price` (DecimalField)  
- `price` (DecimalField)  

**Unique Indexes:**  
- Cart: One menu item per user  
- OrderItem: One menu item per order  

---

## Grading Criteria (Peer Review)
1. Admin can assign users to manager group  
2. Admin can add menu items & categories  
3. Managers can log in, update items, assign delivery crew, manage orders  
4. Delivery crew can access and update assigned orders  
5. Customers can register, log in, browse categories & menu items  
6. Customers can paginate & sort items  
7. Customers can manage cart and place orders  
8. Customers can view their own orders  

---

## Additional Requirements
- Implement filtering, pagination, and sorting for `menu-items` and `orders`  
- Apply throttling for authenticated and unauthenticated users  

---

## Conclusion
You now have the **project scope, models, and endpoints** to implement the Little Lemon API.  
Follow this guide closely to complete your final project successfully.  
Good luck!
