# Create your views here.
from django.shortcuts import render
from django.http import JsonResponse
import requests
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Event,WeatherEvent,FlightList
from datetime import datetime


# Create your views here.
@api_view(['GET'])
def get_events_in_country(request, country):

    current_time = datetime.now().time().hour
    db_data = Event.objects.filter(event_country= country)
    
    
    if db_data:
        x = Event.objects.filter(event_country= country).values()
        y = list(x)
        time_created = y[0]
        
        time_hour = time_created['created_at'].hour
     
        if current_time - time_hour >= 6 :
            response = requests.get(
            url="https://api.predicthq.com/v1/events/",
            headers={
            "Authorization": "Bearer EqpJf87ypBIW6cbbhkXRj_HOyxkNezMRw66NdI86",
            "Accept": "application/json"
            },
            params={
                "country": country,
                "sort":'-local_rank',
                #default limit is 10 
            } )
            
            
            
            events = response.json().get('results', [])
            Event.objects.filter(event_country= country).delete()
            for event in events:
                Event.objects.create(event_name=event['title'],event_id=event['id'],event_country=event['country'],event_date=event['start'],event_lat=event["location"][0],event_lon=event["location"][1],desc= event["description"])
                
            events = Event.objects.filter(event_country= country).values()
            return JsonResponse(list(events),safe=False)
        else:
            events = Event.objects.filter(event_country= country).values()
            return JsonResponse(list(events),safe=False)
    else:
        response = requests.get(
            url="https://api.predicthq.com/v1/events/",
            headers={
            "Authorization": "Bearer EqpJf87ypBIW6cbbhkXRj_HOyxkNezMRw66NdI86",
            "Accept": "application/json"
            },
            params={
                "country": country,
                "sort":'-local_rank',
                #default limit is 10 
            } )
        
        events = response.json().get('results', [])
            
        for event in events:
                Event.objects.create(event_name=event['title'],event_id=event['id'],event_country=event['country'],event_date=event['start'],event_lat=event["location"][0],event_lon=event["location"][1],desc= event["description"])
        events = Event.objects.filter(event_country= country).values()  

        return JsonResponse(list(events),safe=False)


def get_event_wehather(request,eventid):
     current_time = datetime.now().time().hour
     db_data = WeatherEvent.objects.filter(event_id= eventid)
     event = list(Event.objects.filter(event_id = eventid).values())[0]
     lat = event['event_lat']
     lon = event['event_lon']
     url = f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid=f22892654725839a44ff6db985f0b151'

     if db_data:
          if current_time - event['created_at'].hour >= 6:
                res = requests.get(url)
                event_weather = res.json().get('main', [])
                WeatherEvent.objects.filter(event_id= eventid).delete()
                WeatherEvent.objects.create(event_name = event['event_name'],event_Temperature = event_weather["temp"],event_Humidity=event_weather["humidity"],event_id=eventid)
                event_db = WeatherEvent.objects.filter(event_id= eventid).values()
                return JsonResponse(list(event_db),safe=False)
          else:
                event_db = WeatherEvent.objects.filter(event_id= eventid).values()
                return JsonResponse(list(event_db),safe=False)
                    
     else:
            res = requests.get(url)
            event_weather = res.json().get('main', [])
            WeatherEvent.objects.create(event_name = event['event_name'],event_Temperature = event_weather["temp"],event_Humidity=event_weather["humidity"],event_id=eventid)
            event_db = WeatherEvent.objects.filter(event_id= eventid).values()
            return JsonResponse(list(event_db),safe=False)
def get_flight_list(request,eventid,user_airport_code):
     current_time = datetime.now().time().hour
     db_data = FlightList.objects.filter(event_id= eventid)
     event = list(Event.objects.filter(event_id = eventid).values())[0]
     lat = event['event_lat']
     lon = event['event_lon']
     url_to_get_nearby_airports = f'https://airlabs.co/api/v9/nearby?lat={lat}&lng={lon}&distance=200&api_key=500cf030-eb05-4819-aad5-427e4f7572cb'

     if db_data:
          if current_time - event['created_at'].hour >= 6:
            res = requests.get(url_to_get_nearby_airports)
            
            nearby_airportevent_iata_code = res.json().get('response',[])

            if len(nearby_airportevent_iata_code['airports']) >= 1:
                nearby_airportevent_iata_code = nearby_airportevent_iata_code['airports'][0]['iata_code']
            else:
                message ="there is no close airports to the event location by 200km"
                return JsonResponse({"response":message})     

            url_to_get_going_flights = f'https://airlabs.co/api/v9/schedules?dep_iata={user_airport_code}&arr_iata={nearby_airportevent_iata_code}&api_key=500cf030-eb05-4819-aad5-427e4f7572cb'

            res = requests.get(url_to_get_going_flights)

            going_flights_list = res.json().get('response',[])

            if going_flights_list == []:
                going_flights_list =[{"response":"there is no going flights to the event from the user airport!"}]

            url_to_get_backhome_flights = f'https://airlabs.co/api/v9/schedules?dep_iata={nearby_airportevent_iata_code}&arr_iata={user_airport_code}&api_key=500cf030-eb05-4819-aad5-427e4f7572cb'

            res = requests.get(url_to_get_backhome_flights)

            backhome_flights_list = res.json().get('response',[])
            if backhome_flights_list == []:
                backhome_flights_list =[{"response":"there is no going flights to the user airport from the event airport!"}]

            FlightList.objects.filter(event_id= eventid).delete()
            FlightList.objects.create(event_id = eventid,flights_going= going_flights_list, flights_backhome=backhome_flights_list)

            flight_db = FlightList.objects.filter(event_id= eventid).values()
            return JsonResponse(list(flight_db),safe=False)
          
          else:

            flight_db = FlightList.objects.filter(event_id= eventid).values()
            return JsonResponse(list(flight_db),safe=False)
     else: 
            res = requests.get(url_to_get_nearby_airports)
            
            nearby_airportevent_iata_code = res.json().get('response',[])

            if len(nearby_airportevent_iata_code['airports']) >= 1:
                nearby_airportevent_iata_code = nearby_airportevent_iata_code['airports'][0]['iata_code']
            else:
                message ="there is no close airports to the event location by 200km"
                return JsonResponse({"response":message})     

            url_to_get_going_flights = f'https://airlabs.co/api/v9/schedules?dep_iata={user_airport_code}&arr_iata={nearby_airportevent_iata_code}&api_key=500cf030-eb05-4819-aad5-427e4f7572cb'

            res = requests.get(url_to_get_going_flights)

            going_flights_list = res.json().get('response',[])

            if going_flights_list == []:
                going_flights_list =[{"response":"there is no going flights to the event from the user airport!"}]

            url_to_get_backhome_flights = f'https://airlabs.co/api/v9/schedules?dep_iata={nearby_airportevent_iata_code}&arr_iata={user_airport_code}&api_key=500cf030-eb05-4819-aad5-427e4f7572cb'

            res = requests.get(url_to_get_backhome_flights)

            backhome_flights_list = res.json().get('response',[])
            if backhome_flights_list == []:
                backhome_flights_list =[{"response":"there is no going flights to the user airport from the event airport!"}]

            FlightList.objects.create(event_id = eventid,flights_going= going_flights_list, flights_backhome=backhome_flights_list)

            flight_db = FlightList.objects.filter(event_id= eventid).values()
            return JsonResponse(list(flight_db),safe=False)








