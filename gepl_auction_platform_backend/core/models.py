from django.db import models
from pygments.lexers import get_all_lexers
from pygments.styles import get_all_styles

from gepl_auction_platform_backend.users.models import User

LEXERS = [item for item in get_all_lexers() if item[1]]
LANGUAGE_CHOICES = sorted([(item[1][0], item[0]) for item in LEXERS])
STYLE_CHOICES = sorted([(item, item) for item in get_all_styles()])

# Create your models here.


class Teams(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={"user_type": "TEAM OWNER"},
    )
    budget = models.IntegerField(default=500000000)
    logo_url = models.URLField(
        max_length=255,
        blank=True,
        default="https://unsplash.com/photos/white-geometric-stylized-flower-abstract-3d-rendering-art-background-trendy-design-element-modern-minimal-fashion-concept-digital-illustration-OE2dIbtTs7E",
    )

    class Meta:
        ordering = ["name"]
        get_latest_by = "created_at"

    def __str__(self):
        return f"{self.name}"


class Players(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=255)
    role = models.CharField(
        choices=[
            ("BATSMAN", "BATSMAN"),
            ("BOWLER", "BOWLER"),
            ("ALL_ROUNDER", "ALL_ROUNDER"),
            ("WICKET_KEEPER", "WICKET_KEEPER"),
        ],
        max_length=255,
    )
    category = models.CharField(
        choices=[
            ("CATEGORY_A", "CATEGORY_A"),
            ("CATEGORY_B", "CATEGORY_B"),
            ("CATEGORY_C", "CATEGORY_C"),
        ],
        default="CATEGORY_A",
        max_length=255,
    )
    base_price = models.IntegerField(default=0)
    shadow_base_price = models.IntegerField(default=0)
    is_player_auctioned = models.BooleanField(default=False)
    rank = models.IntegerField(default=0)
    is_player_sold = models.BooleanField(default=False)
    team = models.ForeignKey(Teams, on_delete=models.CASCADE, null=True, blank=True)
    profile_picture = models.URLField(
        max_length=255,
        blank=True,
        default="https://unsplash.com/photos/a-man-wearing-a-green-hat-and-a-black-shirt-bw4JnNQ85CM",
    )

    class Meta:
        ordering = ["name"]
        get_latest_by = "created_at"

    def __str__(self):
        return f"{self.name}"


class PlayerStats(models.Model):
    player = models.OneToOneField(Players, primary_key=True, on_delete=models.CASCADE)
    qualifier_wickets = models.IntegerField(default=0)
    qualifier_runs = models.IntegerField(default=0)
    qualifier_matches = models.IntegerField(default=0)

    season_one_wickets = models.IntegerField(default=0)
    season_one_runs = models.IntegerField(default=0)
    season_one_matches = models.IntegerField(default=0)

    class Meta:
        ordering = ["player"]

    def __str__(self):
        return f"{self.player}"


class FrontEndAssets(models.Model):
    id = models.AutoField(primary_key=True)
    asset_name = models.CharField(max_length=255)
    asset_url = models.URLField(max_length=255)

    class Meta:
        ordering = ["asset_name", "id"]

    def __str__(self):
        return f"{self.asset_name}"
