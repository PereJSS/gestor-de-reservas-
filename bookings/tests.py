from datetime import date

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.test import TestCase

from bookings.available_logic import room_booking_is_occupied, room_list_available_by_hotel
from bookings.createService import room_booking_create
from bookings.models import Room, RoomBooking
from core.models import Hotel


def make_hotel(name='Hotel Test'):
    return Hotel.objects.create(
        name=name, address='Calle 1', city='Madrid', country='ES', is_active=True
    )


def make_room(hotel, number='101'):
    return Room.objects.create(
        hotel=hotel, room_number=number, room_type='Doble',
        capacity=2, price_per_night='100.00', is_active=True,
    )


def make_user(username='user_test'):
    return User.objects.create_user(username=username, password='pass1234')



class RoomBookingCreateServiceTest(TestCase):
    def setUp(self):
        self.user = make_user()
        self.hotel = make_hotel()
        self.room = make_room(self.hotel)

    def test_reserva_valida_se_crea(self):
        booking = room_booking_create(
            user=self.user, room=self.room,
            start_date=date(2026, 5, 1), end_date=date(2026, 5, 5),
        )
        self.assertIsNotNone(booking.pk)
        self.assertEqual(RoomBooking.objects.count(), 1)

    def test_fecha_entrada_igual_salida_rechazada(self):
        with self.assertRaises(ValidationError):
            room_booking_create(
                user=self.user, room=self.room,
                start_date=date(2026, 5, 1), end_date=date(2026, 5, 1),
            )

    def test_fecha_entrada_posterior_salida_rechazada(self):
        with self.assertRaises(ValidationError):
            room_booking_create(
                user=self.user, room=self.room,
                start_date=date(2026, 5, 5), end_date=date(2026, 5, 1),
            )

    def test_solapamiento_exacto_rechazado(self):
        room_booking_create(
            user=self.user, room=self.room,
            start_date=date(2026, 5, 1), end_date=date(2026, 5, 5),
        )
        with self.assertRaises(ValidationError):
            room_booking_create(
                user=self.user, room=self.room,
                start_date=date(2026, 5, 1), end_date=date(2026, 5, 5),
            )

    def test_solapamiento_parcial_inicio_rechazado(self):
        room_booking_create(
            user=self.user, room=self.room,
            start_date=date(2026, 5, 1), end_date=date(2026, 5, 5),
        )
        with self.assertRaises(ValidationError):
            room_booking_create(
                user=self.user, room=self.room,
                start_date=date(2026, 5, 3), end_date=date(2026, 5, 8),
            )

    def test_solapamiento_parcial_fin_rechazado(self):
        room_booking_create(
            user=self.user, room=self.room,
            start_date=date(2026, 5, 5), end_date=date(2026, 5, 10),
        )
        with self.assertRaises(ValidationError):
            room_booking_create(
                user=self.user, room=self.room,
                start_date=date(2026, 5, 1), end_date=date(2026, 5, 7),
            )

    def test_reservas_consecutivas_sin_solapamiento_permitidas(self):
        """Salida el día 5 y entrada el mismo día 5 no se solapan."""
        room_booking_create(
            user=self.user, room=self.room,
            start_date=date(2026, 5, 1), end_date=date(2026, 5, 5),
        )
        booking2 = room_booking_create(
            user=self.user, room=self.room,
            start_date=date(2026, 5, 5), end_date=date(2026, 5, 10),
        )
        self.assertIsNotNone(booking2.pk)

    def test_habitaciones_distintas_no_se_bloquean(self):
        room2 = make_room(self.hotel, number='102')
        room_booking_create(
            user=self.user, room=self.room,
            start_date=date(2026, 5, 1), end_date=date(2026, 5, 5),
        )
        booking2 = room_booking_create(
            user=self.user, room=room2,
            start_date=date(2026, 5, 1), end_date=date(2026, 5, 5),
        )
        self.assertIsNotNone(booking2.pk)



class DisponibilidadTest(TestCase):
    def setUp(self):
        self.user = make_user('user_disp')
        self.hotel = make_hotel('Hotel Disp')
        self.room = make_room(self.hotel)

    def test_habitacion_libre_no_esta_ocupada(self):
        result = room_booking_is_occupied(
            room=self.room, start_date=date(2026, 6, 1), end_date=date(2026, 6, 5),
        )
        self.assertFalse(result)

    def test_habitacion_con_reserva_esta_ocupada(self):
        RoomBooking.objects.create(
            user=self.user, room=self.room,
            start_date=date(2026, 6, 1), end_date=date(2026, 6, 5),
        )
        result = room_booking_is_occupied(
            room=self.room, start_date=date(2026, 6, 1), end_date=date(2026, 6, 5),
        )
        self.assertTrue(result)

    def test_room_list_available_devuelve_habitacion_libre(self):
        rooms = room_list_available_by_hotel(
            hotel_id=self.hotel.id,
            start_date=date(2026, 6, 1), end_date=date(2026, 6, 5),
        )
        self.assertIn(self.room, rooms)

    def test_room_list_available_excluye_habitacion_ocupada(self):
        RoomBooking.objects.create(
            user=self.user, room=self.room,
            start_date=date(2026, 6, 1), end_date=date(2026, 6, 5),
        )
        rooms = room_list_available_by_hotel(
            hotel_id=self.hotel.id,
            start_date=date(2026, 6, 1), end_date=date(2026, 6, 5),
        )
        self.assertNotIn(self.room, rooms)

    def test_room_list_available_excluye_habitaciones_inactivas(self):
        self.room.is_active = False
        self.room.save()
        rooms = room_list_available_by_hotel(
            hotel_id=self.hotel.id,
            start_date=date(2026, 6, 1), end_date=date(2026, 6, 5),
        )
        self.assertNotIn(self.room, rooms)


class RoomAvailabilityViewTest(TestCase):
    def setUp(self):
        self.user = make_user('user_calendar')
        self.hotel = make_hotel('Hotel Calendar')
        self.room = make_room(self.hotel, number='201')

    def test_devuelve_dias_no_disponibles_del_mes(self):
        RoomBooking.objects.create(
            user=self.user,
            room=self.room,
            start_date=date(2026, 5, 10),
            end_date=date(2026, 5, 13),
        )

        response = self.client.get(
            reverse('bookings:room-availability'),
            {'room': self.room.id, 'month': '2026-05'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()['unavailable_dates'],
            ['2026-05-10', '2026-05-11', '2026-05-12'],
        )

    def test_falla_si_faltan_parametros(self):
        response = self.client.get(reverse('bookings:room-availability'))

        self.assertEqual(response.status_code, 400)

    def test_formulario_muestra_calendario_inline(self):
        response = self.client.get(reverse('bookings:booking-create'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Calendario de disponibilidad')
        self.assertContains(response, 'data-availability-url')

    def test_disponibilidad_es_publica(self):
        RoomBooking.objects.create(
            user=self.user,
            room=self.room,
            start_date=date(2026, 5, 10),
            end_date=date(2026, 5, 13),
        )

        response = self.client.get(
            reverse('bookings:room-availability'),
            {'room': self.room.id, 'month': '2026-05'},
        )

        self.assertEqual(response.status_code, 200)

    def test_post_sin_login_redirige_a_login(self):
        response = self.client.post(
            reverse('bookings:booking-create'),
            {
                'room': self.room.id,
                'start_date': '2026-05-10',
                'end_date': '2026-05-12',
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('core:user_login'), response.url)
