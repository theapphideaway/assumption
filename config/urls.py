"""URL configuration for the Assumption GOC parish server."""

from django.contrib import admin
from django.urls import path

from parish import api

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/today/", api.today, name="today"),
    path("api/v1/day/<str:iso_date>/", api.day, name="day"),
    path("api/v1/days/", api.days, name="days"),
    path("api/v1/announcements/", api.announcements, name="announcements"),
]
