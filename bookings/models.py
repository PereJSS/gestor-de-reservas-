from django.db import models
from django.contrib.auth.models import User  # Usaremos el modelo oficial de Django
from recurrence.fields import RecurrenceField
from core.models import BaseModel

class Room(BaseModel):
    hotel = models.ForeignKey('core.Hotel', on_delete=models.CASCADE, related_name='rooms')
    room_number = models.CharField(max_length=50) # Quitamos el unique=True de aquí
    # ... resto de campos ...
    room_type = models.CharField(max_length=50) # Ej: Simple, Doble, Suite
    capacity = models.PositiveIntegerField()
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    room_imgs = models.ImageField(upload_to='room_images/', null=True, blank=True)


    class Meta:
        # Permitimos que diferentes hoteles tengan el mismo número de habitación
        unique_together = ('hotel', 'room_number')
        verbose_name = 'Habitación'
        verbose_name_plural = 'Habitaciones'

    @property
    def cover_image(self):
        first_gallery_image = self.images.order_by('position', 'id').first()
        if first_gallery_image and first_gallery_image.image and first_gallery_image.image.storage.exists(first_gallery_image.image.name):
            return first_gallery_image.image
        if self.room_imgs and self.room_imgs.storage.exists(self.room_imgs.name):
            return self.room_imgs
        return None

    def __str__(self):
        return f"{self.hotel.name} - Hab {self.room_number}"


class RoomImage(BaseModel):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='room_images/')
    position = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Imagen de habitación'
        verbose_name_plural = 'Imágenes de habitación'
        ordering = ('position', 'id')

    def __str__(self):
        return f"Imagen de {self.room}"

class RoomBooking(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='bookings')
    start_date = models.DateField()
    end_date = models.DateField()
    recurrence = RecurrenceField(null=True, blank=True)

    class Meta:
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reservas'

    def __str__(self):
        return f"Reserva {self.id}: {self.user.username} en {self.room}"