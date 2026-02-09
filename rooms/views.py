from django.contrib.auth.models import User
from django.db.models import Q
from django.utils.dateparse import parse_date
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Booking, Room
from .serializers import BookingSerializer, RegisterSerializer, RoomSerializer


class RoomViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [AllowAny]

    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = {
        "price_per_day": ["gte", "lte", "exact"],
        "capacity": ["exact", "gte", "lte"],
    }
    ordering_fields = ["price_per_day", "capacity"]

    @action(detail=False, methods=["get"])
    def available(self, request):
        start_date = parse_date(request.query_params.get("start_date"))
        end_date = parse_date(request.query_params.get("end_date"))

        if not start_date or not end_date:
            return Response(
                {"error": "start_date and end_date are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if start_date >= end_date:
            return Response(
                {"error": "End date must be greater than start date"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        booked_rooms = (
            Booking.objects.filter(is_cancelled=False)
            .filter(Q(start_date__lt=end_date) & Q(end_date__gt=start_date))
            .values_list("room_id", flat=True)
        )

        available_rooms = self.filter_queryset(self.get_queryset()).exclude(
            id__in=booked_rooms
        )

        serializer = self.get_serializer(available_rooms, many=True)
        return Response(serializer.data)


class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        booking = self.get_object()
        booking.is_cancelled = True
        booking.save()
        return Response({"status": "booking cancelled"})


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=201)
