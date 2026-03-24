from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import FormView

from bookings.createService import room_booking_create
from bookings.forms import RoomBookingForm
from bookings.models import Room


@method_decorator(login_required, name='dispatch')
class RoomBookingCreateView(FormView):
    template_name = 'bookings/booking_form.html'
    form_class = RoomBookingForm
    success_url = reverse_lazy('core:home')

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