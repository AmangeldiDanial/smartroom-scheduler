from django.urls import path
from .views import dashboard_view
from .views import book_room_view

urlpatterns = [
    path('dashboard/', dashboard_view, name='dashboard'),  # Home page
    path('book/', book_room_view, name='book-room'),
]
