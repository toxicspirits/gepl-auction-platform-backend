from rest_framework import serializers

from gepl_auction_platform_backend.core.models import FrontEndAssets
from gepl_auction_platform_backend.core.models import Players
from gepl_auction_platform_backend.core.models import PlayerStats
from gepl_auction_platform_backend.core.models import Teams
from gepl_auction_platform_backend.users.models import User


class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Players
        fields = [
            "id",
            "name",
            "role",
            "created_at",
            "category",
            "profile_picture",
            "base_price",
            "is_player_sold",
            "team",
            "is_player_auctioned",
            "rank",
        ]


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teams
        fields = ["id", "name", "created_at", "owner", "logo_url", "budget"]


class PlayerStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayerStats
        fields = [
            "player",
            "qualifier_wickets",
            "qualifier_matches",
            "qualifier_runs",
            "season_one_runs",
            "season_one_matches",
            "season_one_wickets",
        ]


class GetPlayerStatsSerializer(serializers.ModelSerializer):
    player_details = PlayerSerializer(many=True, read_only=True)

    class Meta:
        model = PlayerStats
        fields = [
            "player",
            "qualifier_wickets",
            "qualifier_matches",
            "qualifier_runs",
            "season_one_runs",
            "season_one_matches",
            "season_one_wickets",
            "player_details",
        ]


class FrontEndAssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = FrontEndAssets
        fields = ["id", "asset_name", "asset_url"]


class UserTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "name", "user_type", "profile_image"]
