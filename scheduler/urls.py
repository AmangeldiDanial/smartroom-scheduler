from django.urls import path
from .views import dashboard_view, book_room_view, my_bookings_view, cancel_booking_view, export_bookings_csv, bookings_json_view, calendar_view, reports_dashboard, export_report_csv, create_event_view

urlpatterns = [
    path('dashboard/', dashboard_view, name='dashboard'),
    path('book/', book_room_view, name='book-room'),
    path('my-bookings/', my_bookings_view, name='my-bookings'),
    path('my-bookings/<int:booking_id>/cancel/', cancel_booking_view, name='cancel-booking'),
    path('my-bookings/export/', export_bookings_csv, name='export-bookings'),
    path('api/bookings/', bookings_json_view, name='bookings-json'),
    path('calendar/', calendar_view, name='calendar'),
    path('reports/', reports_dashboard, name='reports-dashboard'),
    path('reports/export/', export_report_csv, name='export-reports'),
    path('events/create/', create_event_view, name='create-event'),
]
