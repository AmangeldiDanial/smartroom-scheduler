from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .utils import role_required
from scheduler.forms import BookingForm
from scheduler.models import RoomBooking
from django.contrib import messages

@login_required
def dashboard_view(request):
    return render(request, 'dashboard.html')


@login_required
def book_room_view(request):
    form = BookingForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        new_booking = form.save(commit=False)
        new_booking.user = request.user.user  # Link to custom user

        # Check for conflicts
        conflict = RoomBooking.objects.filter(
            room=new_booking.room,
            timeslot=new_booking.timeslot,
            booking_date=new_booking.booking_date
        ).exists()

        if conflict:
            messages.error(request, "This room is already booked for the selected time.")
        else:
            new_booking.save()
            messages.success(request, "Room successfully booked!")
            return redirect('book-room')

    return render(request, 'book_room.html', {'form': form})