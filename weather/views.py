import logging
from django.shortcuts import render, redirect
from django.http import HttpResponse
import requests
from .models import City
from .forms import CityForm

# Configure logging
logger = logging.getLogger(__name__)

def index(request):
    url_template = 'https://api.openweathermap.org/data/2.5/weather?q={}&appid=2eb27d6e710b8099d34b9413237d0281'

    err_msg = ''
    message = ''
    message_class = ''

    if request.method == 'POST':
        form = CityForm(request.POST)
       
        if form.is_valid():
            new_city = form.cleaned_data['name']
            existing_city_count = City.objects.filter(name=new_city).count()

            if existing_city_count == 0:
                try:
                    r = requests.get(url_template.format(new_city)).json()
                    if r['cod'] == 200:
                        form.save()
                    else:
                        err_msg = 'City does not exist!'
                except requests.exceptions.RequestException as e:
                    err_msg = 'Error fetching data from the weather API.'
            else:
                err_msg = 'City already exists!'

            if err_msg:
                message = err_msg
                message_class = 'is-danger'
            else:
                message = 'City added Successfully!'
                message_class = 'is-success'
    else:
        form = CityForm()

    cities = City.objects.all()
    weather_data = []

    for city in cities:
        try:
            r = requests.get(url_template.format(city)).json()

            # Check if the response contains the necessary keys
            if 'main' in r and 'weather' in r:
                city_weather = {
                    'city': city.name,
                    'temperature': r['main']['temp'],
                    'description': r['weather'][0]['description'],
                    'icon': r['weather'][0]['icon'],
                }
                weather_data.append(city_weather)
            else:
                # Log error if the response format is invalid
                err_msg = f'Error fetching weather data for {city.name}: Invalid response format'
                logger.error(err_msg)
        except requests.exceptions.RequestException as e:
            # Log error if there's an exception during the API request
            err_msg = f'Error fetching weather data for {city.name}: {e}'
            logger.error(err_msg)

    context = {
        'weather_data': weather_data, 
        'form': form,
        'message': message,
        'message_class': message_class
    }
    return render(request, 'weather/weather.html', context)

def delete_city(request, city_name):
    try:
        City.objects.get(name=city_name).delete()
    except City.DoesNotExist:
        pass
    return redirect('home')
def dummy(request):
    return HttpResponse()
