from django.urls import path

from core.views import (
	HotelDetailView,
	HotelListView,
	UserLoginView,
	UserLogoutView,
	UserRegisterView,
)

app_name = 'core'

urlpatterns = [
	path('', HotelListView.as_view(), name='home'),
	path('hoteles/<int:pk>/', HotelDetailView.as_view(), name='hotel-detail'),
	path('auth/login/', UserLoginView.as_view(), name='user_login'),
	path('auth/logout/', UserLogoutView.as_view(), name='user_logout'),
	path('auth/registro/', UserRegisterView.as_view(), name='user_register'),
]
