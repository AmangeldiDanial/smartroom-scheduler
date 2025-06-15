from django.db import models
from django.contrib.auth.models import User as AuthUser
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator


class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    auth_user = models.OneToOneField(AuthUser, on_delete=models.CASCADE, db_column='auth_user_id', null=True)
    username = models.CharField(max_length=50, unique=True)
    role = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'users'

    def __str__(self):
        return self.username


class Room(models.Model):
    room_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    capacity = models.PositiveIntegerField(validators=[MinValueValidator(1)])  # ✅ No negatives or zero
    location = models.CharField(max_length=100, blank=True, null=True)
    type = models.CharField(max_length=50)
    features = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'rooms'

    def __str__(self):
        return self.name


class Timeslot(models.Model):
    timeslot_id = models.AutoField(primary_key=True)
    day = models.CharField(max_length=10)
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        managed = False
        db_table = 'timeslots'

    def clean(self):
        if self.start_time >= self.end_time:
            raise ValidationError("Start time must be before end time.")

    def __str__(self):
        return f"{self.day} {self.start_time}–{self.end_time}"


class Event(models.Model):
    event_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    organizer = models.ForeignKey(User, on_delete=models.DO_NOTHING, db_column='organizer')
    
    class Meta:
        managed = False
        db_table = 'events'

    def __str__(self):
        return self.title


class RoomBooking(models.Model):
    booking_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    room = models.ForeignKey(Room, on_delete=models.DO_NOTHING)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='bookings', null=True)
    timeslot = models.ForeignKey(Timeslot, on_delete=models.DO_NOTHING)
    booking_date = models.DateField()

    class Meta:
        managed = False
        db_table = 'roombookings'
        unique_together = (('room', 'timeslot', 'booking_date'),)

    def __str__(self):
        return f"{self.room.name} on {self.booking_date} @ {self.timeslot}"
