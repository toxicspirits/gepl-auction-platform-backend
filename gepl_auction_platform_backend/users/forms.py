from allauth.account.forms import SignupForm
from allauth.socialaccount.forms import SignupForm as SocialSignupForm
from django import forms as d_forms
from django.contrib.auth import forms as admin_forms
from django.utils.translation import gettext_lazy as _

from gepl_auction_platform_backend.users.models import User


class UserAdminChangeForm(admin_forms.UserChangeForm):
    class Meta(admin_forms.UserChangeForm.Meta):  # type: ignore[name-defined]
        model = User


class UserAdminCreationForm(admin_forms.UserCreationForm):
    """
    Form for User Creation in the Admin Area.
    To change user signup, see UserSignupForm and UserSocialSignupForm.
    """

    class Meta(admin_forms.UserCreationForm.Meta):  # type: ignore[name-defined]
        model = User
        error_messages = {
            "username": {"unique": _("This username has already been taken.")},
        }


class UserSignupForm(SignupForm):
    """
    Form that will be rendered on a user sign up section/screen.
    Default fields will be added automatically.
    Check UserSocialSignupForm for accounts created from social.
    """

    user_type = d_forms.ChoiceField(
        choices=[
            ("SUPER ADMIN", "SUPER_ADMIN"),
            ("AUCTION MANAGER", "AUCTION_MANAGER"),
            ("TEAM OWNER", "TEAM_OWNER"),
            ("SPECTATOR", "SPECTATOR"),
        ],
    )

    def __init__(self, *args, **kwargs):
        # Call the init of the parent class
        super().__init__(*args, **kwargs)

    # Put in custom signup logic
    def custom_signup(self, request, user):
        # Set the user's type from the form reponse
        user.user_type = self.cleaned_data["user_type"]
        # Save the user's type to their database record
        user.save()


class UserSocialSignupForm(SocialSignupForm):
    """
    Renders the form when user has signed up using social accounts.
    Default fields will be added automatically.
    See UserSignupForm otherwise.
    """
