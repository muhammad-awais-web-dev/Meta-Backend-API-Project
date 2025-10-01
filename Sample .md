# 🚀 User Account Management – Little Lemon DRF Exercise

## 📌 Goal
In this exercise, you will use **authentication** and **validation** mechanisms inside **Django REST Framework (DRF)**.

By the end, you will be able to:
- ✅ Add form validators to form data  
- ✅ Perform token and session authentication while using a DRF form  
- ✅ Use the `djoser` and `authtoken` packages for default routes  
- ✅ Use the Django admin panel for creating new users and tokens  

---

## 📖 Introduction
The Little Lemon website has grown in popularity, but **fake reviews** have become a problem.  
You are tasked with **adding security measures** to the review system by implementing authentication and validation.

---

## 🛠️ Setup Instructions

1. Open VS Code and unzip the provided project folder (`LittleLemon` with app `LittleLemonDRF`).
2. Navigate to the directory containing the `Pipfile`.
3. Initialize and install dependencies:

```bash
pipenv shell
pipenv install
```

You should now see `(venv)` in your terminal prompt.

---

## 📂 File Modifications Required
You will mainly update:

- `models.py`
- `serializers.py`
- `settings.py`
- `views.py`
- `urls.py`

---

## 📑 Steps

### **Step 1 – Create Rating Model**
In **models.py**:

```python
from django.db import models
from django.contrib.auth.models import User

class Rating(models.Model):
    menuitem_id = models.SmallIntegerField()
    rating = models.SmallIntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
```

---

### **Step 2 – Create Rating Serializer**
Create a new file **serializers.py** in `LittleLemonDRF/`.

```python
from rest_framework import serializers
from .models import Rating
from rest_framework.validators import UniqueTogetherValidator
from django.contrib.auth.models import User

class RatingSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
```

---

### **Step 3 – Add Meta Class**
Inside **RatingSerializer**:

```python
class Meta:
    model = Rating
    fields = ['user', 'menuitem_id', 'rating']
    validators = [
        UniqueTogetherValidator(
            queryset=Rating.objects.all(),
            fields=['user', 'menuitem_id', 'rating']
        )
    ]
    extra_kwargs = {
        'rating': {
            'max_value': 5,
            'min_value': 0,
        },
    }
```

---

### **Step 4 – Update REST Framework Settings**
In **settings.py**:

```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
}
```

---

### **Step 5 – Add Required Apps**
In **settings.py**, update `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    ...
    'rest_framework.authtoken',
    'djoser',
]
```

---

### **Step 6 – Add Permissions in View**
In **views.py** inside `RatingsView`:

```python
def get_permissions(self):
    if self.request.method == 'GET':
        return []
    return [IsAuthenticated()]
```

---

### **Step 7 – Create Superuser**
Run:

```bash
python manage.py createsuperuser
```

Credentials:

| Field    | Value                       |
|----------|-----------------------------|
| Username | `admin`                     |
| Email    | `admin@littlelemon.com`     |
| Password | `lemon@789!`                |

---

### **Step 8 – Enable Ratings Route**
In **urls.py**, uncomment:

```python
path('ratings', views.RatingsView.as_view()),
```

---

### **Step 9 – Run Migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

---

### **Step 10 – Run Server**
Start development server:

```bash
python manage.py runserver
```

Visit: [http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin)  
Login with superuser credentials.

---

### **Step 11 – Create Users**
Inside Django Admin → Users → Add User:

| Username | Email                  | Password     |
|----------|------------------------|--------------|
| Adrian   | adrian@littlelemon.com | lemon@adr!   |
| Mario    | mario@littlelemon.com  | lemon@mar!   |
| Sana     | sana@littlelemon.com   | lemon@san!   |

---

### **Step 12–13 – Generate Tokens**
Inside Django Admin → Tokens → Add Token:

- Select each user (`Adrian`, `Mario`, `Sana`) and **Save**.  
- Copy and save the generated tokens.

---

### **Step 14 – Test with Insomnia (POST Request)**

**POST** → `http://127.0.0.1:8000/api/ratings`

- **Body (Form URL Encoded):**

| Key         | Value |
|-------------|-------|
| menuitem_id | 3     |
| rating      | 4     |

- **Auth Header:**

```
Authorization: Token <user_token>
```

Example JSON Response:

```json
{
  "user": 2,
  "menuitem_id": 3,
  "rating": 4
}
```

---

### **Step 15 – Validate Duplicate Rating**
If the same user tries to rate the same item again:

```json
{
  "non_field_errors": [
    "The fields user, menuitem_id, rating must make a unique set."
  ]
}
```

---

### **Step 16 – Allow Different Users**
If a **different user** rates the same item → success.

Example:

```json
{
  "user": 3,
  "menuitem_id": 3,
  "rating": 5
}
```

---

### **Step 17 – View Ratings**
Visit:  
[http://127.0.0.1:8000/api/ratings](http://127.0.0.1:8000/api/ratings)  

You should see all reviews listed.

---

## ✅ Conclusion
In this exercise, you:

- Implemented **authentication** with Tokens and Sessions  
- Used **Djoser** for default routes  
- Created **validators** to prevent duplicate ratings  
- Secured the review system with **throttling and unique constraints**  
