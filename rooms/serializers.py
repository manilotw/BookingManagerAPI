from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.db.models import Q
from rest_framework import serializers

from .models import Booking, Room


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ("id", "name", "price_per_day", "capacity")


class BookingSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Booking
        fields = (
            "id",
            "room",
            "user",
            "start_date",
            "end_date",
            "is_cancelled",
        )
        read_only_fields = ("is_cancelled",)

    def validate(self, attrs):
        start_date = attrs["start_date"]
        end_date = attrs["end_date"]

        if start_date >= end_date:
            raise serializers.ValidationError(
                "End date must be greater than start date"
            )

        return attrs


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("id", "username", "password")

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"], password=validated_data["password"]
        )
        return user
