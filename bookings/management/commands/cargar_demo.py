from datetime import date, timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from bookings.models import Room, RoomBooking
from core.models import Hotel, UserProfile


class Command(BaseCommand):
    help = 'Crea datos de demostración: superusuario admin, hoteles, habitaciones y reservas.'

    def handle(self, *args, **options):
        self._crear_superusuario()
        self._crear_usuario_demo()
        hotel1 = self._crear_hotel(
            name='Hotel Mediterráneo',
            address='Paseo Marítimo, 12',
            city='Barcelona',
            country='ES',
            description='Hotel de lujo frente al mar con vistas panorámicas.',
        )
        hotel2 = self._crear_hotel(
            name='Hotel Sierra Nevada',
            address='Calle Mayor, 5',
            city='Granada',
            country='ES',
            description='Alojamiento en plena naturaleza con acceso directo a las pistas.',
        )
        self._crear_habitaciones(hotel1)
        self._crear_habitaciones(hotel2)
        self._crear_reserva()
        self.stdout.write(self.style.SUCCESS('Datos de demo cargados correctamente.'))
        self.stdout.write('')
        self.stdout.write('  Admin panel : /admin/')
        self.stdout.write('  Usuario     : admin')
        self.stdout.write('  Contraseña  : Admin1234!')

    def _crear_superusuario(self):
        if User.objects.filter(username='admin').exists():
            self.stdout.write('  Superusuario "admin" ya existe, se omite.')
            return
        User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='Admin1234!',
        )
        self.stdout.write('  Superusuario "admin" creado.')

    def _crear_usuario_demo(self):
        if User.objects.filter(username='demo').exists():
            return
        user = User.objects.create_user(
            username='demo',
            email='demo@example.com',
            password='Demo1234!',
        )
        UserProfile.objects.get_or_create(user=user)
        self.stdout.write('  Usuario "demo" creado.')

    def _crear_hotel(self, **kwargs):
        hotel, created = Hotel.objects.get_or_create(name=kwargs['name'], defaults=kwargs)
        if created:
            self.stdout.write(f'  Hotel "{hotel.name}" creado.')
        return hotel

    def _crear_habitaciones(self, hotel):
        habitaciones = [
            {'room_number': '101', 'room_type': 'Individual', 'capacity': 1, 'price_per_night': '75.00'},
            {'room_number': '201', 'room_type': 'Doble', 'capacity': 2, 'price_per_night': '120.00'},
            {'room_number': '301', 'room_type': 'Suite', 'capacity': 4, 'price_per_night': '220.00'},
        ]
        for datos in habitaciones:
            room, created = Room.objects.get_or_create(
                hotel=hotel,
                room_number=datos['room_number'],
                defaults={**datos, 'is_active': True},
            )
            if created:
                self.stdout.write(f'  Habitación {room.room_number} en {hotel.name} creada.')

    def _crear_reserva(self):
        user = User.objects.filter(username='demo').first()
        room = Room.objects.filter(room_type='Doble').first()
        if not user or not room:
            return
        today = date.today()
        start = today + timedelta(days=7)
        end = today + timedelta(days=10)
        if not RoomBooking.objects.filter(user=user, room=room, start_date=start).exists():
            RoomBooking.objects.create(user=user, room=room, start_date=start, end_date=end)
            self.stdout.write(f'  Reserva de demo creada ({start} → {end}).')
