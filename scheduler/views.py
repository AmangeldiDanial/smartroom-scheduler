from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .utils import role_required
from scheduler.forms import BookingForm, EventForm
from scheduler.models import RoomBooking, Room, Timeslot, Event
from django.contrib import messages
import csv
from django.http import HttpResponse, JsonResponse
import datetime
from django.db.models import Count, F
from django.db.models.functions import ExtractWeekDay
import calendar

@login_required
def dashboard_view(request):
    return render(request, 'dashboard.html')

@login_required
@role_required(['Faculty', 'Administrator'])
def book_room_view(request):
    selected_date_str = request.GET.get('date') or request.POST.get('booking_date')
    selected_date = None

    if selected_date_str:
        try:
            selected_date = datetime.datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        except ValueError:
            selected_date = None

    if not Event.objects.filter(organizer=request.user.user).exists():
        messages.error(request, "You must create an event before booking a room.")
        return redirect('dashboard')

    form = BookingForm(request.POST or None, date=selected_date, user=request.user.user)

    if request.method == 'POST' and form.is_valid():
        new_booking = form.save(commit=False)
        new_booking.user = request.user.user
        new_booking.booking_date = selected_date

        room_conflict = RoomBooking.objects.filter(
            room=new_booking.room,
            timeslot=new_booking.timeslot,
            booking_date=new_booking.booking_date
        ).exists()

        user_conflict = RoomBooking.objects.filter(
            user=new_booking.user,
            timeslot=new_booking.timeslot,
            booking_date=new_booking.booking_date
        ).exists()

        if room_conflict:
            messages.error(request, "This room is already booked for the selected time.")
        elif user_conflict:
            messages.error(request, "❌ You already have a booking at that time.")
        else:
            new_booking.save()
            messages.success(request, "Room successfully booked!")
            return redirect('book-room')

    return render(request, 'book_room.html', {'form': form, 'selected_date': selected_date})

@login_required
@role_required(['Faculty', 'Administrator'])
def my_bookings_view(request):
    custom_user = request.user.user
    bookings = RoomBooking.objects.filter(user=custom_user).select_related('room', 'timeslot', 'event')

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
@role_required(['Faculty', 'Administrator'])
def cancel_booking_view(request, booking_id):
    custom_user = request.user.user
    booking = get_object_or_404(RoomBooking, pk=booking_id, user=custom_user)

    if request.method == 'POST':
        booking.delete()
        messages.success(request, "Booking cancelled successfully.")
        return redirect('my-bookings')

    return render(request, 'cancel_booking_confirm.html', {'booking': booking})

@login_required
@role_required(['Faculty', 'Administrator', 'Staff'])
def export_bookings_csv(request):
    custom_user = request.user.user
    bookings = RoomBooking.objects.filter(user=custom_user).select_related('room', 'timeslot', 'event')

    # Apply same filters
    room_id = request.GET.get('room')
    day = request.GET.get('day')
    sort = request.GET.get('sort', 'desc')

    if room_id and room_id.isdigit():
        bookings = bookings.filter(room_id=int(room_id))

    if day and day.lower() != 'none':
        bookings = bookings.filter(timeslot__day=day)

    if sort == 'asc':
        bookings = bookings.order_by('booking_date')
    else:
        bookings = bookings.order_by('-booking_date')

    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="my_bookings.csv"'

    writer = csv.writer(response)
    writer.writerow(['Event Title', 'Room', 'Date', 'Day', 'Start Time', 'End Time'])

    for b in bookings:
        writer.writerow([
            b.event.title,
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

    bookings = RoomBooking.objects.select_related('room', 'timeslot', 'user', 'event')

    events = []
    for booking in bookings:
        is_yours = booking.user == user
        color = 'green' if is_yours else 'gray'

        # Build datetime from booking_date + timeslot time
        start = datetime.datetime.combine(booking.booking_date, booking.timeslot.start_time)
        end = datetime.datetime.combine(booking.booking_date, booking.timeslot.end_time)

        events.append({
            'title': booking.event.title,
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
                'label': f"{'You' if is_yours else 'Booked'} – {booking.room.name}"
            }
        })

    return JsonResponse(events, safe=False)

@login_required
def calendar_view(request):
    return render(request, 'calendar.html')

@login_required
@role_required(['Faculty', 'Administrator', 'Staff'])
def reports_dashboard(request):
    room_stats = (
        RoomBooking.objects.values('room__name')
        .annotate(bookings=Count('room'))
        .order_by('-bookings')
    )

    room_labels = [entry['room__name'] for entry in room_stats]
    room_counts = [entry['bookings'] for entry in room_stats]

    # 📅 Weekday usage stats
    weekday_stats = (
        RoomBooking.objects
        .annotate(weekday=ExtractWeekDay('booking_date'))  # 1=Sunday, 7=Saturday
        .values('weekday')
        .annotate(total=Count('booking_id'))
        .order_by('weekday')
    )

    # Convert numeric weekdays to names
    weekday_labels = [calendar.day_name[(entry['weekday'] - 1) % 7] for entry in weekday_stats]
    weekday_counts = [entry['total'] for entry in weekday_stats]

    # --- Timeslot usage ---
    slot_stats = (
        RoomBooking.objects
        .values('timeslot_id', 'timeslot__day', 'timeslot__start_time', 'timeslot__end_time')
        .annotate(bookings=Count('booking_id'))
        .order_by('timeslot__day', 'timeslot__start_time')
    )

    slot_labels = [
        f"{entry['timeslot__day']} {entry['timeslot__start_time'].strftime('%H:%M')}–{entry['timeslot__end_time'].strftime('%H:%M')}"
        for entry in slot_stats
    ]
    slot_counts = [entry['bookings'] for entry in slot_stats]


    return render(request, 'reports_dashboard.html', {
        'room_labels': room_labels,
        'room_counts': room_counts,
        'weekday_labels': weekday_labels,
        'weekday_counts': weekday_counts,
        'slot_labels': slot_labels,
        'slot_counts': slot_counts,
    })

@login_required
@role_required(['Faculty', 'Administrator', 'Staff'])
def export_report_csv(request):
    # Query room usage
    room_stats = (
        RoomBooking.objects.values('room__name')
        .annotate(bookings=Count('room'))
        .order_by('-bookings')
    )

    # Query weekday usage
    weekday_stats = (
        RoomBooking.objects
        .annotate(weekday=ExtractWeekDay('booking_date'))
        .values('weekday')
        .annotate(total=Count('booking_id'))
        .order_by('weekday')
    )

    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="booking_report.csv"'

    writer = csv.writer(response)

    # Room Usage Section
    writer.writerow(['Room Usage Report'])
    writer.writerow(['Room Name', 'Booking Count'])
    for entry in room_stats:
        writer.writerow([entry['room__name'], entry['bookings']])
    writer.writerow([])  # Blank line

    # Weekday Usage Section
    writer.writerow(['Bookings by Day of Week'])
    writer.writerow(['Day', 'Booking Count'])
    import calendar
    for entry in weekday_stats:
        day_name = calendar.day_name[(entry['weekday'] - 1) % 7]
        writer.writerow([day_name, entry['total']])

    return response

@login_required
@role_required(['Faculty', 'Administrator', 'Staff'])
def timeslot_report_view(request):
    # Group bookings by timeslot and weekday (1=Sunday, 7=Saturday)
    stats = (
        RoomBooking.objects
        .annotate(weekday=ExtractWeekDay('booking_date'))
        .values('timeslot__day', 'timeslot__start_time', 'timeslot__end_time', 'weekday')
        .annotate(bookings=Count('booking_id'))
        .order_by('weekday', 'timeslot__start_time')
    )

    # Format data for chart: { "Monday 09:00–10:00": count, ... }
    slot_labels = []
    slot_counts = []

    for entry in stats:
        day_name = calendar.day_name[(entry['weekday'] - 1) % 7]
        time_range = f"{entry['timeslot__start_time'].strftime('%H:%M')}–{entry['timeslot__end_time'].strftime('%H:%M')}"
        label = f"{day_name} {time_range}"
        slot_labels.append(label)
        slot_counts.append(entry['bookings'])

    return render(request, 'timeslot_report.html', {
        'slot_labels': slot_labels,
        'slot_counts': slot_counts,
    })

@login_required
@role_required(['Faculty', 'Administrator'])
def create_event_view(request):
    form = EventForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        event = form.save(commit=False)
        event.organizer = request.user.user  # Link to custom User table
        event.save()
        messages.success(request, "✅ Event created successfully.")
        return redirect('dashboard')

    return render(request, 'create_event.html', {'form': form})