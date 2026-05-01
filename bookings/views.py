import calendar
from datetime import date
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.views import redirect_to_login
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import FormView

from bookings.createService import room_booking_create
from bookings.forms import RoomBookingForm
from bookings.models import Room, RoomBooking


class RoomBookingCreateView(FormView):
    template_name = 'bookings/booking_form.html'
    form_class = RoomBookingForm
    success_url = reverse_lazy('core:home')

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())
        return super().post(request, *args, **kwargs)

    def get_initial(self):
        initial = super().get_initial()
        room_id = self.request.GET.get('room')

        if room_id:
            room = Room.objects.filter(pk=room_id, is_active=True).first()
            if room:
                initial['room'] = room

        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        if start_date:
            initial['start_date'] = start_date
        if end_date:
            initial['end_date'] = end_date

        return initial

    def form_valid(self, form):
        data = form.cleaned_data

        try:
            room_booking_create(
                user=self.request.user,
                room=data['room'],
                start_date=data['start_date'],
                end_date=data['end_date'],
                recurrence=data.get('recurrence'),
            )
            messages.success(self.request, '¡Reserva creada con éxito! Te esperamos.')
            return super().form_valid(form)
        except Exception as exc:
            form.add_error(None, str(exc))
            return self.form_invalid(form)

def room_availability_view(request):
    room_id = request.GET.get('room')
    month = request.GET.get('month')

    if not room_id or not month:
        return JsonResponse(
            {'error': 'Debes indicar habitacion y mes.'},
            status=400,
        )

    try:
        room = Room.objects.get(pk=room_id, is_active=True)
    except Room.DoesNotExist:
        return JsonResponse({'error': 'Habitacion no encontrada.'}, status=404)

    try:
        year, month_number = [int(value) for value in month.split('-', 1)]
        first_day = date(year, month_number, 1)
    except (TypeError, ValueError):
        return JsonResponse({'error': 'Mes invalido.'}, status=400)

    _, month_days = calendar.monthrange(year, month_number)
    last_day = date(year, month_number, month_days)

    bookings = RoomBooking.objects.filter(
        room=room,
        start_date__lte=last_day,
        end_date__gt=first_day,
    ).values('start_date', 'end_date')

    unavailable_dates = []
    for booking in bookings:
        current_day = max(booking['start_date'], first_day)
        last_unavailable_day = min(booking['end_date'], last_day)
        while current_day < last_unavailable_day:
            unavailable_dates.append(current_day.isoformat())
            current_day += timedelta(days=1)

    return JsonResponse(
        {
            'room': room.id,
            'month': first_day.strftime('%Y-%m'),
            'unavailable_dates': unavailable_dates,
        }
    )