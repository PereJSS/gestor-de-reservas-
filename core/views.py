from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView

from core.forms import UserRegisterForm
from core.models import UserProfile
from core.selectors import hotel_detail_get, hotel_list_visible


class HotelListView(ListView):
    template_name = 'home.html'
    context_object_name = 'hotels'

    def get_queryset(self):
        return hotel_list_visible()


class HotelDetailView(DetailView):
    template_name = 'core/hotel_detail.html'
    context_object_name = 'hotel'

    def get_object(self):
        return hotel_detail_get(hotel_id=self.kwargs.get('pk'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        start_str = self.request.GET.get('start_date', '')
        end_str = self.request.GET.get('end_date', '')
        filtered = False

        if start_str and end_str:
            try:
                from datetime import date as date_type
                from bookings.available_logic import room_list_available_by_hotel
                start_date = date_type.fromisoformat(start_str)
                end_date = date_type.fromisoformat(end_str)
                if start_date < end_date:
                    context['rooms'] = room_list_available_by_hotel(
                        hotel_id=self.object.id,
                        start_date=start_date,
                        end_date=end_date,
                    ).order_by('room_number')
                    filtered = True
            except ValueError:
                pass

        if not filtered:
            context['rooms'] = self.object.rooms.filter(is_active=True).order_by('room_number')

        context['start_date'] = start_str
        context['end_date'] = end_str
        context['filtered'] = filtered
        return context


class UserLoginView(LoginView):
    template_name = 'auth/login.html'
    redirect_authenticated_user = True
    next_page = reverse_lazy('core:home')


class UserLogoutView(LogoutView):
    next_page = reverse_lazy('core:home')


class UserRegisterView(CreateView):
    template_name = 'auth/register.html'
    form_class = UserRegisterForm
    success_url = reverse_lazy('core:home')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

    def handle_no_permission(self):
        from django.shortcuts import redirect

        return redirect('core:home')

    def form_valid(self, form):
        response = super().form_valid(form)
        UserProfile.objects.get_or_create(user=self.object)
        login(self.request, self.object)
        return response