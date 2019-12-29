from rest_framework import serializers
from users.serializers import UserSerializer
from .models import Room


class RoomSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Room
        exclude = ("modified",)
        read_only_fields = (
            "user",
            "id",
            "created",
            "updated",
        )

    def validate(self, data):
        if self.instance:  # if update a room
            check_in = data.get("check_in", self.instance.check_in)
            check_out = data.get("check_out", self.instance.check_out)
        else:  # if create a room
            check_in = data.get("check_in")
            check_out = data.get("check_out")
        if check_in == check_out:
            raise serializers.ValidationError(
                "Not enough time between check_in and check_out"
            )
        return data
