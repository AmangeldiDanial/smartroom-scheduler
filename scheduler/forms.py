from django import forms
from scheduler.models import RoomBooking

class BookingForm(forms.ModelForm):
    class Meta:
        model = RoomBooking
        fields = ['room', 'timeslot', 'booking_date']
        widgets = {
            'booking_date': forms.DateInput(attrs={'type': 'date'})
        }
