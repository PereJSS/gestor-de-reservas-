from datetime import date

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from bookings.models import Room, RoomBooking
from core.models import Hotel, UserProfile


def make_hotel(name='Hotel Vista', active=True):
    return Hotel.objects.create(
        name=name, address='Calle 1', city='Barcelona', country='ES', is_active=active,
    )


def make_room(hotel, number='101'):
    return Room.objects.create(
        hotel=hotel, room_number=number, room_type='Simple',
        capacity=1, price_per_night='80.00', is_active=True,
    )


def make_user(username='viewer'):
    return User.objects.create_user(username=username, password='pass1234')



class HomeViewTest(TestCase):
    def test_home_carga_correctamente(self):
        resp = self.client.get(reverse('core:home'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'home.html')

    def test_home_muestra_hoteles_activos(self):
        h = make_hotel('Hotel Activo')
        resp = self.client.get(reverse('core:home'))
        self.assertContains(resp, 'Hotel Activo')

    def test_home_no_muestra_hoteles_inactivos(self):
        make_hotel('Hotel Oculto', active=False)
        resp = self.client.get(reverse('core:home'))
        self.assertNotContains(resp, 'Hotel Oculto')



class HotelDetailViewTest(TestCase):
    def setUp(self):
        self.hotel = make_hotel()
        self.room = make_room(self.hotel)
        self.url = reverse('core:hotel-detail', kwargs={'pk': self.hotel.pk})

    def test_detalle_hotel_carga(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'core/hotel_detail.html')

    def test_detalle_muestra_habitaciones_activas(self):
        resp = self.client.get(self.url)
        self.assertIn(self.room, resp.context['rooms'])
        self.assertFalse(resp.context['filtered'])

    def test_detalle_hotel_inexistente_devuelve_404(self):
        resp = self.client.get(reverse('core:hotel-detail', kwargs={'pk': 99999}))
        self.assertEqual(resp.status_code, 404)

    def test_filtro_fechas_validas_activa_disponibilidad(self):
        resp = self.client.get(self.url + '?start_date=2026-07-01&end_date=2026-07-05')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.context['filtered'])
        self.assertIn(self.room, resp.context['rooms'])

    def test_filtro_fechas_con_habitacion_ocupada(self):
        user = make_user('ocupante')
        RoomBooking.objects.create(
            user=user, room=self.room,
            start_date=date(2026, 7, 1), end_date=date(2026, 7, 5),
        )
        resp = self.client.get(self.url + '?start_date=2026-07-01&end_date=2026-07-05')
        self.assertTrue(resp.context['filtered'])
        self.assertNotIn(self.room, resp.context['rooms'])

    def test_filtro_fechas_invalidas_no_filtra(self):
        resp = self.client.get(self.url + '?start_date=no-es-fecha&end_date=tampoco')
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(resp.context['filtered'])



class BookingCreateViewTest(TestCase):
    def setUp(self):
        self.user = make_user('reservador')
        self.hotel = make_hotel('Hotel Booking')
        self.room = make_room(self.hotel)
        self.url = reverse('bookings:booking-create')

    def test_reserva_requiere_login(self):
        resp = self.client.get(self.url)
        self.assertRedirects(resp, f'/auth/login/?next={self.url}', fetch_redirect_response=False)

    def test_reserva_formulario_carga_autenticado(self):
        self.client.login(username='reservador', password='pass1234')
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'bookings/booking_form.html')

    def test_reserva_preselecciona_habitacion_y_fechas(self):
        self.client.login(username='reservador', password='pass1234')
        resp = self.client.get(
            self.url + f'?room={self.room.pk}&start_date=2026-08-01&end_date=2026-08-05'
        )
        self.assertEqual(resp.status_code, 200)
        form = resp.context['form']
        self.assertEqual(form.initial.get('room'), self.room)
        self.assertEqual(form.initial.get('start_date'), '2026-08-01')

    def test_post_reserva_valida_redirige_a_exito(self):
        self.client.login(username='reservador', password='pass1234')
        resp = self.client.post(self.url, {
            'room': self.room.pk,
            'start_date': '2026-08-01',
            'end_date': '2026-08-05',
        }, follow=True)
        self.assertRedirects(resp, reverse('core:home'))
        self.assertEqual(RoomBooking.objects.count(), 1)
        self.assertContains(resp, 'Reserva creada con')

    def test_post_reserva_con_solapamiento_muestra_error(self):
        RoomBooking.objects.create(
            user=self.user, room=self.room,
            start_date=date(2026, 8, 1), end_date=date(2026, 8, 5),
        )
        self.client.login(username='reservador', password='pass1234')
        resp = self.client.post(self.url, {
            'room': self.room.pk,
            'start_date': '2026-08-01',
            'end_date': '2026-08-05',
        })
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(resp.context['form'].is_valid())
        self.assertEqual(RoomBooking.objects.count(), 1)

    def test_post_fechas_invalidas_muestra_error(self):
        self.client.login(username='reservador', password='pass1234')
        resp = self.client.post(self.url, {
            'room': self.room.pk,
            'start_date': '2026-08-05',
            'end_date': '2026-08-01',
        })
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(resp.context['form'].is_valid())
        self.assertEqual(RoomBooking.objects.count(), 0)



class AuthViewsTest(TestCase):
    def test_login_carga(self):
        resp = self.client.get(reverse('core:user_login'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'auth/login.html')

    def test_registro_carga(self):
        resp = self.client.get(reverse('core:user_register'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'auth/register.html')

    def test_registro_crea_usuario_y_perfil(self):
        resp = self.client.post(reverse('core:user_register'), {
            'username': 'nuevo_usuario',
            'email': 'nuevo@example.com',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
        })
        self.assertRedirects(resp, reverse('core:home'))
        self.assertTrue(User.objects.filter(username='nuevo_usuario').exists())
        self.assertTrue(
            UserProfile.objects.filter(user__username='nuevo_usuario').exists()
        )

    def test_usuario_autenticado_no_puede_ver_registro(self):
        make_user('ya_registrado')
        self.client.login(username='ya_registrado', password='pass1234')
        resp = self.client.get(reverse('core:user_register'))
        self.assertRedirects(resp, reverse('core:home'))
