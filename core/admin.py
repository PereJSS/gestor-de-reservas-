from django.contrib import admin
from django.contrib.admin.sites import NotRegistered
from bookings.models import Room as BookingRoom
from core.models import Hotel, HotelImage, UserProfile


class FriendlyLabelsMixin:
	field_labels = {}

	def formfield_for_dbfield(self, db_field, request, **kwargs):
		formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
		if formfield and db_field.name in self.field_labels:
			formfield.label = self.field_labels[db_field.name]
		return formfield


class HotelRoomInline(FriendlyLabelsMixin, admin.TabularInline):
	model = BookingRoom
	extra = 1
	fields = ('room_number', 'room_type', 'capacity', 'price_per_night', 'is_active', 'room_imgs')
	verbose_name = 'Habitación'
	verbose_name_plural = 'Habitaciones del hotel'
	field_labels = {
		'room_number': 'Número',
		'room_type': 'Tipo',
		'capacity': 'Capacidad',
		'price_per_night': 'Precio por noche',
		'is_active': 'Activa',
		'room_imgs': 'Imagen',
	}


class HotelImageInline(FriendlyLabelsMixin, admin.TabularInline):
	model = HotelImage
	extra = 1
	fields = ('image', 'position')
	verbose_name = 'Imagen adicional'
	verbose_name_plural = 'Galería del hotel'
	field_labels = {
		'image': 'Imagen',
		'position': 'Orden',
	}

@admin.register(Hotel)
class HotelAdmin(FriendlyLabelsMixin, admin.ModelAdmin):
	list_display = ('id', 'name', 'city', 'country', 'is_active', 'created_at')
	list_filter = ('is_active', 'city', 'country', 'created_at')
	search_fields = ('name', 'city', 'country', 'address')
	ordering = ('name',)
	inlines = [HotelImageInline, HotelRoomInline]
	field_labels = {
		'name': 'Nombre del hotel',
		'address': 'Dirección',
		'city': 'Ciudad',
		'country': 'País',
		'description': 'Descripción',
		'is_active': 'Activo',
		'hotel_img': 'Imagen del hotel',
	}
	fieldsets = (
		('Información principal', {'fields': ('name', 'description', 'is_active')}),
		('Ubicación', {'fields': ('address', 'city', 'country')}),
		('Multimedia', {'fields': ('hotel_img',)}),
	)
@admin.register(UserProfile)
class UserProfileAdmin(FriendlyLabelsMixin, admin.ModelAdmin):
	list_display = ('id', 'user', 'phone_number', 'created_at')
	search_fields = ('user__username', 'user__email', 'phone_number', 'address')
	ordering = ('user__username',)
	field_labels = {
		'user': 'Usuario',
		'phone_number': 'Teléfono',
		'address': 'Dirección',
		'user_profile_img': 'Foto de perfil',
	}
	fieldsets = (
		('Usuario', {'fields': ('user',)}),
		('Datos de contacto', {'fields': ('phone_number', 'address')}),
		('Imagen', {'fields': ('user_profile_img',)}),
	)


admin.site.site_header = 'Panel de gestión de reservas'
admin.site.site_title = 'Gestor de reservas'
admin.site.index_title = 'Administración'


try:
	from schedule.forms import EventAdminForm
	from schedule.models import Calendar, CalendarRelation, Event, EventRelation, Occurrence, Rule

	for model in (Calendar, CalendarRelation, EventRelation, Event, Occurrence, Rule):
		try:
			admin.site.unregister(model)
		except NotRegistered:
			pass

	@admin.register(Calendar)
	class AgendaCalendarAdmin(FriendlyLabelsMixin, admin.ModelAdmin):
		list_display = ('nombre', 'slug')
		prepopulated_fields = {'slug': ('name',)}
		search_fields = ['name']
		fieldsets = (('Datos del calendario', {'fields': [('name', 'slug')]}),)
		field_labels = {
			'name': 'Nombre',
			'slug': 'Identificador (slug)',
		}

		@admin.display(description='Nombre', ordering='name')
		def nombre(self, obj):
			return obj.name

	@admin.register(CalendarRelation)
	class AgendaCalendarRelationAdmin(FriendlyLabelsMixin, admin.ModelAdmin):
		list_display = ('calendario', 'objeto_relacionado', 'heredable')
		list_filter = ('inheritable',)
		fieldsets = (
			(
				'Datos de la relación',
				{
					'fields': [
						'calendar',
						('content_type', 'object_id', 'distinction'),
						'inheritable',
					]
				},
			),
		)
		field_labels = {
			'calendar': 'Calendario',
			'content_type': 'Tipo de contenido',
			'object_id': 'ID del objeto',
			'distinction': 'Distinción',
			'inheritable': 'Heredable',
		}

		@admin.display(description='Calendario', ordering='calendar')
		def calendario(self, obj):
			return obj.calendar

		@admin.display(description='Objeto relacionado')
		def objeto_relacionado(self, obj):
			return obj.content_object

		@admin.display(description='Heredable', ordering='inheritable')
		def heredable(self, obj):
			return obj.inheritable

	@admin.register(EventRelation)
	class AgendaEventRelationAdmin(FriendlyLabelsMixin, admin.ModelAdmin):
		list_display = ('evento', 'objeto_relacionado', 'distincion')
		fieldsets = (
			(
				'Datos de la relación',
				{'fields': ['event', ('content_type', 'object_id', 'distinction')]},
			),
		)
		field_labels = {
			'event': 'Evento',
			'content_type': 'Tipo de contenido',
			'object_id': 'ID del objeto',
			'distinction': 'Distinción',
		}

		@admin.display(description='Evento', ordering='event')
		def evento(self, obj):
			return obj.event

		@admin.display(description='Objeto relacionado')
		def objeto_relacionado(self, obj):
			return obj.content_object

		@admin.display(description='Distinción', ordering='distinction')
		def distincion(self, obj):
			return obj.distinction

	@admin.register(Event)
	class AgendaEventAdmin(FriendlyLabelsMixin, admin.ModelAdmin):
		list_display = ('titulo', 'inicio', 'fin', 'calendario')
		list_filter = ('start', 'calendar')
		ordering = ('-start',)
		date_hierarchy = 'start'
		search_fields = ('title', 'description')
		fieldsets = (
			(
				'Datos del evento',
				{
					'fields': [
						('title', 'color_event'),
						('description',),
						('start', 'end'),
						('creator', 'calendar'),
						('rule', 'end_recurring_period'),
					]
				},
			),
		)
		field_labels = {
			'title': 'Título',
			'color_event': 'Color del evento',
			'description': 'Descripción',
			'start': 'Inicio',
			'end': 'Fin',
			'creator': 'Creador',
			'calendar': 'Calendario',
			'rule': 'Regla de repetición',
			'end_recurring_period': 'Fin de recurrencia',
		}
		form = EventAdminForm

		@admin.display(description='Título', ordering='title')
		def titulo(self, obj):
			return obj.title

		@admin.display(description='Inicio', ordering='start')
		def inicio(self, obj):
			return obj.start

		@admin.display(description='Fin', ordering='end')
		def fin(self, obj):
			return obj.end

		@admin.display(description='Calendario', ordering='calendar')
		def calendario(self, obj):
			return obj.calendar

	@admin.register(Occurrence)
	class AgendaOccurrenceAdmin(FriendlyLabelsMixin, admin.ModelAdmin):
		list_display = ('evento', 'titulo', 'inicio', 'fin', 'cancelada')
		list_filter = ('cancelled', 'start')
		ordering = ('-start',)
		search_fields = ('title', 'description', 'event__title')
		field_labels = {
			'event': 'Evento',
			'title': 'Título',
			'description': 'Descripción',
			'start': 'Inicio',
			'end': 'Fin',
			'cancelled': 'Cancelada',
			'original_start': 'Inicio original',
			'original_end': 'Fin original',
		}

		@admin.display(description='Evento', ordering='event')
		def evento(self, obj):
			return obj.event

		@admin.display(description='Título', ordering='title')
		def titulo(self, obj):
			return obj.title

		@admin.display(description='Inicio', ordering='start')
		def inicio(self, obj):
			return obj.start

		@admin.display(description='Fin', ordering='end')
		def fin(self, obj):
			return obj.end

		@admin.display(description='Cancelada', ordering='cancelled')
		def cancelada(self, obj):
			return obj.cancelled

	@admin.register(Rule)
	class AgendaRuleAdmin(FriendlyLabelsMixin, admin.ModelAdmin):
		list_display = ('nombre', 'frecuencia')
		list_filter = ('frequency',)
		search_fields = ('name', 'description')
		field_labels = {
			'name': 'Nombre',
			'description': 'Descripción',
			'frequency': 'Frecuencia',
			'params': 'Parámetros',
		}

		@admin.display(description='Nombre', ordering='name')
		def nombre(self, obj):
			return obj.name

		@admin.display(description='Frecuencia', ordering='frequency')
		def frecuencia(self, obj):
			return obj.frequency

except Exception:
	pass
