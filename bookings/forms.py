from django import forms
from bookings.models import Room, RoomBooking

class RoomBookingForm(forms.ModelForm):
    class Meta:
        model = RoomBooking
        fields = ['room', 'start_date', 'end_date', 'recurrence']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'room': forms.Select(attrs={'class': 'form-select'}),
        }