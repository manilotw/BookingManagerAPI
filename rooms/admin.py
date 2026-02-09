from django.contrib import admin

from .models import Room


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "price_per_day", "capacity")
    list_filter = ("capacity",)
    search_fields = ("name",)


from .models import Booking, Room


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("id", "room", "user", "start_date", "end_date", "is_cancelled")
    list_filter = ("is_cancelled", "start_date")
    search_fields = ("room__name", "user__username")
