"""URL configuration for the Assumption GOC parish server."""

from django.contrib import admin
from django.urls import path

from parish import api
from prayers import api as prayer_api
from prayers import scripture_api

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/today/", api.today, name="today"),
    path("api/v1/day/<str:iso_date>/", api.day, name="day"),
    path("api/v1/days/", api.days, name="days"),
    path("api/v1/announcements/", api.announcements, name="announcements"),
    path("api/v1/prayers/", prayer_api.prayers, name="prayers"),
    path("api/v1/scripture/books/", scripture_api.books, name="books"),
    path("api/v1/scripture/search/", scripture_api.search, name="search"),
    path("api/v1/scripture/<str:book>/<int:number>/", scripture_api.chapter,
         name="chapter"),
]
