from django.db import models
from django.contrib.auth import get_user_model
# Create your models here.

class Event(models.Model):
    event_name = models.CharField(max_length=64)
    event_id = models.CharField(max_length=64)
    event_date = models.CharField(max_length=64)
    event_country = models.CharField(max_length=64,default="peaky")
    event_lat = models.FloatField() 
    event_lon = models.FloatField() 
    desc = models.TextField()
    created_at = models.TimeField(auto_now_add=True)
    



    def __str__(self):
        return self.nameOfEvent
    
class WeatherEvent(models.Model):
       event_name = models.CharField(max_length=64) 
       event_id = models.CharField(max_length=64)
       event_Temperature = models.FloatField()
       event_Humidity = models.FloatField()

class FlightList(models.Model):
       event_id = models.CharField(max_length=64)
       flights_going = models.JSONField()
       flights_backhome = models.JSONField()


