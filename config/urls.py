"""URL configuration for the Assumption GOC parish server."""

from django.contrib import admin
from django.urls import path

from parish import api
from prayers import api as prayer_api

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/today/", api.today, name="today"),
    path("api/v1/day/<str:iso_date>/", api.day, name="day"),
    path("api/v1/days/", api.days, name="days"),
    path("api/v1/announcements/", api.announcements, name="announcements"),
    path("api/v1/prayers/", prayer_api.prayers, name="prayers"),
]
