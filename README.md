# EVENTS API Documentation

## Sample of queries:

### insert this before the link: http://127.0.0.1:8000/

### endpoints:

- list/country_code/ ---> this will return the top ten events in the country.
- weather/eventid/ ---> this will return the weather of the location of the event.
- flights/eventid/user_airport_code/ ---> this will return the list of depurture flights from the user airport to the nearest airport to the event and the back flight to the user airport from the event airport.

## Steps to Execute

- run the 'pip install -r requirements.txt'
- run the 'python manage.py runserver'