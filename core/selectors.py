from django.shortcuts import get_object_or_404
from core.models import Hotel
from django.db.models import QuerySet


def hotel_detail_get(*, hotel_id: int) -> Hotel:
    return get_object_or_404(Hotel, id=hotel_id)


def hotel_list_visible() -> QuerySet[Hotel]:
    return Hotel.objects.filter(is_active=True).order_by('name')