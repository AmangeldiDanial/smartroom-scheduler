from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .utils import role_required
from scheduler.forms import BookingForm
from scheduler.models import RoomBooking, Room, Timeslot
from django.contrib import messages
import csv
from django.http import HttpResponse, JsonResponse
import datetime

@login_required
def dashboard_view(request):
    return render(request, 'dashboard.html')

@login_required
@role_required(['Faculty', 'Admin'])
def book_room_view(request):
    selected_date_str = request.GET.get('date') or request.POST.get('booking_date')
    selected_date = None

    if selected_date_str:
        try:
            selected_date = datetime.datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        except ValueError:
            selected_date = None

    form = BookingForm(request.POST or None, date=selected_date)

    if request.method == 'POST' and form.is_valid():
        new_booking = form.save(commit=False)
        new_booking.user = request.user.user
        new_booking.booking_date = selected_date

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

    return render(request, 'book_room.html', {'form': form, 'selected_date': selected_date})

@login_required
def my_bookings_view(request):
    custom_user = request.user.user
    bookings = RoomBooking.objects.filter(user=custom_user).select_related('room', 'timeslot')

    # Filtering
    room_id = request.GET.get('room')
    day = request.GET.get('day')
    sort = request.GET.get('sort', 'desc')

    if room_id:
        bookings = bookings.filter(room_id=room_id)

    if day:
        bookings = bookings.filter(timeslot__day=day)

    if sort == 'asc':
        bookings = bookings.order_by('booking_date')
    else:
        bookings = bookings.order_by('-booking_date')

    rooms = Room.objects.all()
    days = Timeslot.objects.values_list('day', flat=True).distinct()

    return render(request, 'my_bookings.html', {
        'bookings': bookings,
        'rooms': rooms,
        'days': days,
        'selected_room': room_id,
        'selected_day': day,
        'sort': sort
    })


@login_required
def cancel_booking_view(request, booking_id):
    custom_user = request.user.user
    booking = get_object_or_404(RoomBooking, pk=booking_id, user=custom_user)

    if request.method == 'POST':
        booking.delete()
        messages.success(request, "Booking cancelled successfully.")
        return redirect('my-bookings')

    return render(request, 'cancel_booking_confirm.html', {'booking': booking})

@login_required
def export_bookings_csv(request):
    custom_user = request.user.user
    bookings = RoomBooking.objects.filter(user=custom_user).select_related('room', 'timeslot')

    # Apply same filters
    room_id = request.GET.get('room')
    day = request.GET.get('day')
    sort = request.GET.get('sort', 'desc')

    if room_id:
        bookings = bookings.filter(room_id=room_id)
    if day:
        bookings = bookings.filter(timeslot__day=day)
    if sort == 'asc':
        bookings = bookings.order_by('booking_date')
    else:
        bookings = bookings.order_by('-booking_date')

    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="my_bookings.csv"'

    writer = csv.writer(response)
    writer.writerow(['Room', 'Date', 'Day', 'Start Time', 'End Time'])

    for b in bookings:
        writer.writerow([
            b.room.name,
            b.booking_date,
            b.timeslot.day,
            b.timeslot.start_time,
            b.timeslot.end_time
        ])

    return response

@login_required
def bookings_json_view(request):
    user = request.user.user

    bookings = RoomBooking.objects.select_related('room', 'timeslot', 'user')

    events = []
    for booking in bookings:
        is_yours = booking.user == user
        color = 'green' if is_yours else 'gray'

        # Build datetime from booking_date + timeslot time
        start = datetime.datetime.combine(booking.booking_date, booking.timeslot.start_time)
        end = datetime.datetime.combine(booking.booking_date, booking.timeslot.end_time)

        events.append({
            'title': f"{'You' if is_yours else 'Booked'} – {booking.room.name}",
            'start': start.isoformat(),
            'end': end.isoformat(),
            'color': color,
            'id': booking.booking_id,
            'extendedProps': {
                'is_yours': is_yours,
                'room': booking.room.name,
                'date': booking.booking_date.isoformat(),
                'day': booking.timeslot.day,
                'start_time': booking.timeslot.start_time.strftime('%H:%M'),
                'end_time': booking.timeslot.end_time.strftime('%H:%M'),
            }
        })

    return JsonResponse(events, safe=False)

@login_required
def calendar_view(request):
    return render(request, 'calendar.html')
