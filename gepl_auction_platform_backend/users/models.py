from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import CharField
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Default custom user model for gepl-auction-platform-backend.
    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """

    # First and last name do not cover name patterns around the globe
    name = CharField(_("Name of User"), blank=True, max_length=255)
    first_name = None  # type: ignore[assignment]
    last_name = None  # type: ignore[assignment]
    user_type = models.CharField(
        choices=[
            ("SUPER ADMIN", "SUPER_ADMIN"),
            ("AUCTION MANAGER", "AUCTION_MANAGER"),
            ("TEAM OWNER", "TEAM_OWNER"),
            ("SPECTATOR", "SPECTATOR"),
        ],
        default="SUPER_ADMIN",
    )

    profile_image = models.URLField(
        _("Profile image"),
        blank=True,
        default="https://django-backend-services.s3.eu-west-1.amazonaws.com/player-profile/GEPL-Player-Bidding-Screen-V3.jpg",
    )

    def get_absolute_url(self) -> str:
        """Get URL for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"username": self.username})

    def __str__(self):
        return f"{self.username}"
