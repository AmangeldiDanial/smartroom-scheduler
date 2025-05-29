from django import forms
from scheduler.models import RoomBooking, Timeslot
from django.core.exceptions import ValidationError
import datetime

class BookingForm(forms.ModelForm):
    class Meta:
        model = RoomBooking
        fields = ['room', 'timeslot']
        widgets = {
            'booking_date': forms.DateInput(attrs={'type': 'date'})
        }
    
    def __init__(self, *args, **kwargs):
        date = kwargs.pop('date', None)
        super().__init__(*args, **kwargs)

        if date:
            day = date.strftime('%A')  # e.g., 'Monday'
            self.fields['timeslot'].queryset = Timeslot.objects.filter(day=day)
        else:
            self.fields['timeslot'].queryset = Timeslot.objects.none()  # hide until date is selected
    
    def clean(self):
        cleaned_data = super().clean()
        booking_date = cleaned_data.get('booking_date')
        timeslot = cleaned_data.get('timeslot')

        if booking_date and timeslot:
            weekday_str = booking_date.strftime('%A')  # e.g. 'Monday', 'Tuesday'

            if weekday_str != timeslot.day:
                raise ValidationError(
                    f"The selected date is a {weekday_str}, but the timeslot is for {timeslot.day}."
                )
