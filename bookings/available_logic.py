from datetime import date
from django.db.models import QuerySet
from bookings.models import Room, RoomBooking


def room_booking_is_occupied(*, room: Room, start_date: date, end_date: date) -> bool:
    """Comprueba si la habitacion esta ocupada en el rango de fechas."""
    return RoomBooking.objects.filter(
        room=room,
        start_date__lt=end_date,
        end_date__gt=start_date,
    ).exists()


def room_list_available_by_hotel(*, hotel_id: int, start_date: date, end_date: date) -> QuerySet[Room]:
    """Lista habitaciones libres para un hotel especifico en fechas concretas."""
    occupied_ids = RoomBooking.objects.filter(
        room__hotel_id=hotel_id,
        start_date__lt=end_date,
        end_date__gt=start_date,
    ).values_list('room_id', flat=True)

    return Room.objects.filter(hotel_id=hotel_id, is_active=True).exclude(id__in=occupied_ids)
