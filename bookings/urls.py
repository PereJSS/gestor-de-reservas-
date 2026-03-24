from django.http import HttpResponse
from django.urls import path

from bookings.views import RoomBookingCreateView

app_name = 'bookings'


def booking_success_view(request):
	return HttpResponse('Reserva creada con exito.')


urlpatterns = [
	path('crear/', RoomBookingCreateView.as_view(), name='booking-create'),
	path('exito/', booking_success_view, name='booking-success'),
]
