from django.shortcuts import get_object_or_404
from bookings.models import RoomBooking
from bookings.models import Room

def room_detail_get(*, room_id: int) -> Room:
    return get_object_or_404(Room.objects.select_related('hotel'), id=room_id)


def room_booking_is_occupied(*, room: Room, start_date, end_date) -> bool:
    return RoomBooking.objects.filter(
        room=room,
        start_date__lt=end_date,
        end_date__gt=start_date,
    ).exists()
