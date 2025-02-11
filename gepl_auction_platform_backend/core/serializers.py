from rest_framework import serializers

from gepl_auction_platform_backend.core.models import Players
from gepl_auction_platform_backend.core.models import Teams


class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Players
        fields = ["id", "name", "role", "base_price", "stats", "shadow_base_price"]


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teams
        fields = ["id", "name", "owner", "budget"]
