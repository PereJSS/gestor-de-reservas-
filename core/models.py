from django.db import models
from django.contrib.auth.models import User  # Usaremos el modelo oficial de Django


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

# Hotel: Ahora con imagen y descripción como pediste
class Hotel(BaseModel):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    hotel_img = models.ImageField(upload_to='hotel_images/', null=True, blank=True)

    class Meta:
        verbose_name = 'Hotel'
        verbose_name_plural = 'Hoteles'

    @property
    def cover_image(self):
        first_gallery_image = self.images.order_by('position', 'id').first()
        if first_gallery_image and first_gallery_image.image and first_gallery_image.image.storage.exists(first_gallery_image.image.name):
            return first_gallery_image.image
        if self.hotel_img and self.hotel_img.storage.exists(self.hotel_img.name):
            return self.hotel_img
        return None
    
    def __str__(self):
        return self.name


class HotelImage(BaseModel):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='hotel_images/')
    position = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Imagen de hotel'
        verbose_name_plural = 'Imágenes de hotel'
        ordering = ('position', 'id')

    def __str__(self):
        return f"Imagen de {self.hotel.name}"

# UserProfile: Para guardar los datos extra del usuario (teléfono, dirección, foto)
class UserProfile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    user_profile_img = models.ImageField(upload_to='profile_images/', null=True, blank=True)

    class Meta:
        verbose_name = 'Perfil de usuario'
        verbose_name_plural = 'Perfiles de usuario'
    
    def __str__(self):
        return f"Perfil de {self.user.username}"