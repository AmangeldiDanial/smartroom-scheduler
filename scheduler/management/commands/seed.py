from django.core.management.base import BaseCommand
from scheduler.models import Room, Timeslot, RoomBooking, User
from faker import Faker
from random import choice
from datetime import timedelta, date, time
from django.utils import timezone
import calendar

fake = Faker()

class Command(BaseCommand):
    help = "Seed the database with fake but valid room bookings"

    def handle(self, *args, **kwargs):
        # Create sample rooms if none exist
        if Room.objects.count() == 0:
            Room.objects.create(name="Room A", capacity=20, location="Building 1", type="Lecture", features="Projector")
            Room.objects.create(name="Room B", capacity=30, location="Building 2", type="Meeting", features="TV, Whiteboard")
            Room.objects.create(name="Conference Hall", capacity=100, location="Main Floor", type="Event", features="Mic, Stage")
            self.stdout.write(self.style.SUCCESS("Sample rooms created."))

        # Create timeslots if none exist
        if Timeslot.objects.count() == 0:
            days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
            for day in days:
                Timeslot.objects.get_or_create(day=day, start_time=time(9, 0), end_time=time(10, 0))
                Timeslot.objects.get_or_create(day=day, start_time=time(10, 0), end_time=time(11, 0))
            self.stdout.write(self.style.SUCCESS("Sample timeslots created."))

        # Only use faculty/admins for bookings
        users = User.objects.filter(role__in=["Faculty", "Admin"])
        if not users.exists():
            self.stdout.write(self.style.WARNING("No faculty or admin users found. Please create some first."))
            return

        rooms = list(Room.objects.all())
        timeslots = list(Timeslot.objects.all())

        created = 0
        attempts = 0
        today = date.today()

        while created < 30 and attempts < 100:
            user = choice(users)
            room = choice(rooms)
            slot = choice(timeslots)

            # Get next date that matches timeslot.day
            days_ahead = (list(calendar.day_name).index(slot.day) - today.weekday()) % 7
            booking_date = today + timedelta(days=days_ahead + choice([0, 7, 14]))  # up to 2 weeks ahead

            # Check for conflict
            if not RoomBooking.objects.filter(room=room, timeslot=slot, booking_date=booking_date).exists():
                RoomBooking.objects.create(
                    user=user,
                    room=room,
                    timeslot=slot,
                    booking_date=booking_date
                )
                created += 1
            attempts += 1

        self.stdout.write(self.style.SUCCESS(f"Seeded {created} valid, conflict-free bookings."))

