from django.contrib import admin
from bookings.models import Room, RoomBooking, RoomImage


class FriendlyLabelsMixin:
	field_labels = {}

	def formfield_for_dbfield(self, db_field, request, **kwargs):
		formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
		if formfield and db_field.name in self.field_labels:
			formfield.label = self.field_labels[db_field.name]
		return formfield


class RoomBookingInline(FriendlyLabelsMixin, admin.TabularInline):
	model = RoomBooking
	extra = 1
	fields = ('user', 'start_date', 'end_date', 'recurrence')
	verbose_name = 'Reserva'
	verbose_name_plural = 'Reservas de la habitación'
	field_labels = {
		'user': 'Cliente',
		'start_date': 'Entrada',
		'end_date': 'Salida',
		'recurrence': 'Recurrencia',
	}


class RoomImageInline(FriendlyLabelsMixin, admin.TabularInline):
	model = RoomImage
	extra = 1
	fields = ('image', 'position')
	verbose_name = 'Imagen adicional'
	verbose_name_plural = 'Galería de la habitación'
	field_labels = {
		'image': 'Imagen',
		'position': 'Orden',
	}


@admin.register(Room)
class RoomAdmin(FriendlyLabelsMixin, admin.ModelAdmin):
	list_display = ('id', 'hotel', 'room_number', 'room_type', 'capacity', 'price_per_night', 'is_active')
	list_filter = ('is_active', 'room_type', 'hotel')
	search_fields = ('room_number', 'room_type', 'hotel__name')
	ordering = ('hotel__name', 'room_number')
	inlines = [RoomImageInline, RoomBookingInline]
	field_labels = {
		'hotel': 'Hotel',
		'room_number': 'Número de habitación',
		'room_type': 'Tipo de habitación',
		'capacity': 'Capacidad',
		'price_per_night': 'Precio por noche',
		'is_active': 'Disponible',
		'room_imgs': 'Imagen de la habitación',
	}
	fieldsets = (
		('Datos de la habitación', {'fields': ('hotel', 'room_number', 'room_type')}),
		('Capacidad y precio', {'fields': ('capacity', 'price_per_night')}),
		('Estado e imagen', {'fields': ('is_active', 'room_imgs')}),
	)


@admin.register(RoomBooking)
class RoomBookingAdmin(FriendlyLabelsMixin, admin.ModelAdmin):
	list_display = ('id', 'user', 'room', 'start_date', 'end_date', 'created_at')
	list_filter = ('start_date', 'end_date', 'created_at')
	search_fields = ('user__username', 'room__room_number', 'room__hotel__name')
	date_hierarchy = 'start_date'
	ordering = ('-start_date',)
	field_labels = {
		'user': 'Cliente',
		'room': 'Habitación',
		'start_date': 'Fecha de entrada',
		'end_date': 'Fecha de salida',
		'recurrence': 'Recurrencia',
	}
	fieldsets = (
		('Datos de la reserva', {'fields': ('user', 'room')}),
		('Fechas', {'fields': ('start_date', 'end_date', 'recurrence')}),
	)
