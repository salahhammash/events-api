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
#decorator is commonly used in web development frameworks like Django or Django REST Framework to define API endpoints 
def get_events_in_country(request, country):

    current_time = datetime.now().time().hour
    # datetime is a module in Python's standard library that provides classes for working with dates and times.
    #.now : to take the present time /datetime.now() returns a datetime object representing the current date and time
    #.time() is a method of the datetime object that extracts the time portion from the datetime object and returns a time object.
    #hour is an attribute of the time object that retrieves the hour value as an integer
    '''
    first gets the current date and time, then extracts the time part, and finally retrieves the hour value. As a result, current_time will contain the current hour of the day as an integer.
    '''
    
    db_data = Event.objects.filter(event_country= country)
    # to take the data that inside the EVENT model
    # In summary its retrieves all event objects from the database that have a matching country value specified by the country variable and stores them in the db_data variable.
    
    
    if db_data:
        x = Event.objects.filter(event_country= country).values()
        # retrieves all the matching events from the database with the specified country and returns a QuerySet of dictionaries. Each dictionary represents an event and contains key-value pairs for its attributes.
        y = list(x)
        # converts the QuerySet into a list. This step is done to make it easier to access the individual dictionaries.
        time_created = y[0]
        #  retrieves the first dictionary from the y list, which corresponds to the first event in the QuerySet.
        
        time_hour = time_created['created_at'].hour
        # accesses the value of the 'created_at' key in the time_created dictionary.-- then retrieves the hour value from the timestamp.
        
     
        if current_time - time_hour >= 6 :
            # calculates the difference between the current hour and the hour value extracted from the timestamp (time_hour)
            '''
          if the time difference between the current time and the hour value extracted from the timestamp is 6 hours or more, the code sends a GET request to the specified API endpoint to retrieve event data for the specified country, potentially sorting the events based on a 'local_rank' attribute.
            '''
            response = requests.get(
            url="https://api.predicthq.com/v1/events/",
            headers={
            "Authorization": "Bearer EqpJf87ypBIW6cbbhkXRj_HOyxkNezMRw66NdI86",
            "Accept": "application/json"
            },
            params={
                "country": country,
                # is a parameter that likely specifies the country for which events should be retrieved.
                "sort":'-local_rank',
                # is a paramiter that may indicate sorting the events based on the 'local_rank' attribute in descending order
              
            } )
            # sends an HTTP GET request to the specified URLto retrieve event data.
            
            
            
            events = response.json().get('results', [])
            # extracts the JSON response from the response object obtained from the API request , It tries to retrieve the value associated with the key 'results' in the JSON response. If the key is not found, it sets events to an empty list [].
            
            Event.objects.filter(event_country= country).delete()
            #  deletes all events in the database that match the specified country. This clears the existing events before adding the new events retrieved from the API.
            
            for event in events:
                Event.objects.create(event_name=event['title'],event_id=event['id'],event_country=event['country'],event_date=event['start'],event_lat=event["location"][0],event_lon=event["location"][1],desc= event["description"])
                #  Event objects in the database for each event retrieved from the API. The attributes of the new event objects are populated with values from the corresponding fields in the event dictionary.
                
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








