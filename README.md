# SmartRoom Scheduler

SmartRoom Scheduler is a web-based room timetable management system built with Django and PostgreSQL. It helps universities or organizations manage room bookings, avoid scheduling conflicts, and visualize availability with a user-friendly interface.

---

## 🚀 Features

- Role-based login system (Admin, Faculty, Staff)
- Secure authentication using Django's built-in auth system
- Room, timeslot, and event management via admin panel
- Personalized dashboard showing user bookings
- Conflict-free room booking logic
- Logout, login redirection, and user-session support

---

## 🧱 Tech Stack

- **Backend**: Django 4.x
- **Database**: PostgreSQL
- **Frontend**: Django templates + Bootstrap (optional)
- **Authentication**: Django's `auth_user`, linked to custom `users` table
- **Deployment-ready**: Configurable with Gunicorn, Nginx, or Render

---

## 🖥️ Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/AmangeldiDanial/smartroom-scheduler.git
   cd smartroom-scheduler

2. **Create and activate virtual environment**
    ```bash
    python -m venv venv
    source venv/Scripts/activate  # On Windows

4. **Install dependencies**
    ```bash
    pip install -r requirements.txt
    Configure PostgreSQL settings in settings.py

6. **Configure PostgreSQL settings in settings.py**
   ```python
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'your_db_name',
            'USER': 'your_db_user',
            'PASSWORD': 'your_password',
            'HOST': 'localhost',
            'PORT': '5432',
        }
    }

8. **Run migrations**
    ```bash
    python manage.py migrate

10. **Create a superuser**
    ```bash
    python manage.py createsuperuser

12. **Start the development server**
    ```bash
    python manage.py runserver

## 👥 User Roles

| Role    | Description                                     |
|---------|-------------------------------------------------|
| **Admin**   | Full access to all rooms and data              |
| **Faculty** | Can book and manage their own events          |
| **Staff**   | Can manage timeslots and process room requests |


## 🔐 Login Info
You can log in at:
http://localhost:8000/accounts/login/

And access the admin panel at:
http://localhost:8000/admin/

## 🗃️ Project Structure
$ ./smartroom-scheduler .
.
 * [scheduler/](./scheduler) # Django app with models, views, templates
 * [smartroom/](./smartroom) # Project settings and URLs
 * [templates/](./templates) # Global HTML templates
 * [static/](./static) # (optional) CSS/JS assets
 * [venv/](./venv)  # Python virtual environment (not tracked)
 * [manage.py](./manage.py)

##📌 License
This project is for academic use and learning purposes.
---
