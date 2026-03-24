from datetime import date

from django.core.exceptions import ValidationError

from bookings.models import Room, RoomBooking
from bookings.selectors import room_booking_is_occupied


def room_booking_create(*, user, room: Room, start_date: date, end_date: date, recurrence=None) -> RoomBooking:
    if start_date >= end_date:
        raise ValidationError('La fecha de entrada debe ser anterior a la de salida.')

    if room_booking_is_occupied(room=room, start_date=start_date, end_date=end_date):
        raise ValidationError(f'La habitacion {room.room_number} ya esta reservada para esas fechas.')

    booking = RoomBooking(
        user=user,
        room=room,
        start_date=start_date,
        end_date=end_date,
        recurrence=recurrence,
    )
    booking.full_clean()
    booking.save()
    return booking