# ruff: noqa
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include
from django.urls import path
from django.views import defaults as default_views
from django.views.generic import TemplateView
from drf_spectacular.views import SpectacularAPIView
from drf_spectacular.views import SpectacularSwaggerView
from rest_framework.authtoken.views import obtain_auth_token
from gepl_auction_platform_backend.core.admin import event_admin_site
from gepl_auction_platform_backend.core import views
from django.urls import re_path


urlpatterns = [
    path("", TemplateView.as_view(template_name="pages/home.html"), name="home"),
    path(
        "about/",
        TemplateView.as_view(template_name="pages/about.html"),
        name="about",
    ),
    # Django Admin, use {% url 'admin:index' %}
    path(settings.ADMIN_URL, admin.site.urls),
    path("auction-admin/", event_admin_site.urls),
    # User management
    path(
        "users/", include("gepl_auction_platform_backend.users.urls", namespace="users")
    ),
    path("accounts/", include("allauth.urls")),
    # Your stuff: custom urls includes go here
    # ...
    re_path(r"^users/?$", views.UserTypeView.as_view()),
    # Media files
    # path("event-admin/", include(event_admin_site.urls, namespace="event-admin")),
    *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
]
if settings.DEBUG:
    # Static file serving when using Gunicorn + Uvicorn for local web socket development
    urlpatterns += staticfiles_urlpatterns()

# API URLS
urlpatterns += [
    # API base url
    path("api/", include("config.api_router")),
    path("api/auth/", include("djoser.urls")),
    path("api/auth/", include("djoser.urls.jwt")),
    # DRF auth token
    path("api/auth-token/", obtain_auth_token),
    path("api/schema/", SpectacularAPIView.as_view(), name="api-schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="api-schema"),
        name="api-docs",
    ),
    path("api/teams/", views.TeamList.as_view()),
    path("api/teams/<int:pk>/", views.TeamDetail.as_view()),
    path("api/players/", views.PlayerList.as_view()),
    path("api/teams/<int:pk>/players/", views.PlayerInTeamView.as_view()),
    path("api/players/<int:pk>/", views.PlayerDetail.as_view()),
    re_path(r"^api/category/?$", views.CategoryPlayers.as_view()),
    path(r"api/player/<int:pk>/stats/", views.PlayerStatsDetail.as_view()),
    re_path(r"^api/frontend/assets/?$", views.FrontEndAsset.as_view()),
    # path("ws/chat/", bidding.ChatConsumer.as_asgi()),
    path("bidding_room/", include("gepl_auction_platform_backend.bidding_room.urls")),
]

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
