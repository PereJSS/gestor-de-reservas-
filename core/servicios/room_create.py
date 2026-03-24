from bookings.models import Room

def room_create(*, hotel, room_number, room_type, capacity, price_per_night, room_imgs=None) -> Room:
    """Servicio para registrar una habitación en un hotel[cite: 130]."""
    room = Room(
        hotel=hotel,
        room_number=room_number,
        room_type=room_type,
        capacity=capacity,
        price_per_night=price_per_night,
        room_imgs=room_imgs
    )
    room.full_clean()
    room.save()
    return room