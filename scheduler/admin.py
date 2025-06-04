from django.contrib import admin
from .models import User, Room, Timeslot, Event, RoomBooking


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'username', 'email', 'role')
    search_fields = ('username', 'email')
    list_filter = ('role',)


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('room_id', 'name', 'capacity', 'location', 'type', 'features')
    search_fields = ('name', 'location')
    list_filter = ('type',)


@admin.register(Timeslot)
class TimeslotAdmin(admin.ModelAdmin):
    list_display = ('timeslot_id', 'day', 'start_time', 'end_time')
    list_filter = ('day',)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('event_id', 'title', 'organizer', 'start_date', 'end_date')
    search_fields = ('title',)
    list_filter = ('start_date',)


@admin.register(RoomBooking)
class RoomBookingAdmin(admin.ModelAdmin):
    list_display = ('booking_id', 'user', 'room', 'timeslot', 'booking_date')
    list_filter = ('booking_date', 'room', 'timeslot')
    search_fields = ('user__username',)
