from django.contrib.admin import AdminSite
from django.contrib.admin import ModelAdmin

from gepl_auction_platform_backend.core.models import Players
from gepl_auction_platform_backend.core.models import PlayerStats
from gepl_auction_platform_backend.core.models import Teams
from gepl_auction_platform_backend.users.models import User

# Register your models here.


class AdminSite(AdminSite):
    site_header = "GEPL Auctions Admin"
    site_title = "GEPL Auctions Admin Portal"
    index_title = "Welcome to GEPL Auctions Admin Portal"


class TeamsAdmin(ModelAdmin):
    list_display = ["name", "owner", "budget"]
    search_fields = ["name"]
    list_filter = ["owner"]


class PlayersAdmin(ModelAdmin):
    list_display = ["name", "category", "team"]
    search_fields = ["name"]
    list_filter = ("is_player_sold", "category")


event_admin_site = AdminSite(name="auction-admin")
event_admin_site.register(Players, PlayersAdmin)
event_admin_site.register(Teams, TeamsAdmin)
event_admin_site.register(User)
event_admin_site.register(PlayerStats)
