from django.urls import path
from .views import get_events_in_country,get_event_wehather,get_flight_list

urlpatterns = [
    path('<str:country>', get_events_in_country, name='event_list'),
    path('list/<str:eventid>', get_event_wehather, name='event_weather'),
    path('flight/<str:eventid>/<str:user_airport_code>', get_flight_list, name='event_flight'),
]