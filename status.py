import requests
import time
from datetime import datetime
from pytz import timezone
import os

discord_token = os.getenv("DISCORD_TOKEN")
weather_api_key = os.getenv("WEATHER_API_KEY")
latitude = float(os.getenv("LATITUDE"))
longitude = float(os.getenv("LONGITUDE"))

local_tz = timezone("Europe/Berlin")

def change_status(token, message):
    headers = {'authorization': token}
    json_data = {
        "custom_status": {"text": message}
    }
    requests.patch("https://discord.com/api/v10/users/@me/settings", headers=headers, json=json_data)

def get_current_time():
    current_time = datetime.now(local_tz)
    return current_time.strftime("%H:%M")

def get_weather_emoji(weather_main, current_time, sunrise_time, sunset_time):
    if sunrise_time is None or sunset_time is None:
        is_daytime = True
    else:
        is_daytime = sunrise_time <= current_time < sunset_time

    weather_to_emoji = {
        "Clear": "☀️" if is_daytime else "🌙",
        "Clouds": "☁️",
        "Rain": "🌧️",
        "Drizzle": "🌦️",
        "Thunderstorm": "⛈️",
        "Snow": "❄️"
    }
    return weather_to_emoji.get(weather_main, "🌙" if not is_daytime else "☀️")

def get_weather_and_sun_times():
    weather_url = f"http://api.weatherapi.com/v1/current.json?key={weather_api_key}&q={latitude},{longitude}&aqi=no"
    response = requests.get(weather_url)
    if response.status_code == 200:
        weather_data = response.json()
        try:
            weather_main = weather_data['current']['condition']['text']
            return weather_main
        except (KeyError, ValueError) as e:
            print(f"Error parsing weather data: {e}")
    else:
        print(f"Weather API error: {response.status_code} - {response.text}")
    return "Clear"

def get_sun_times():
    sun_url = f"https://api.sunrisesunset.io/json?lat={latitude}&lng={longitude}"
    response = requests.get(sun_url)
    if response.status_code == 200:
        sun_data = response.json()
        try:
            sunrise_time = datetime.strptime(sun_data['results']['sunrise'], '%I:%M:%S %p').strftime('%H:%M')
            sunset_time = datetime.strptime(sun_data['results']['sunset'], '%I:%M:%S %p').strftime('%H:%M')
            return datetime.strptime(sunrise_time, '%H:%M').time(), datetime.strptime(sunset_time, '%H:%M').time()
        except (KeyError, ValueError) as e:
            print(f"Error parsing sun times data: {e}")
    else:
        print(f"Sun times API error: {response.status_code} - {response.text}")
    return None, None

previous_status = None
last_weather_update = time.time()
last_sun_update = 0
sunrise_time, sunset_time = get_sun_times()

while True:
    current_time = get_current_time()
    if time.time() - last_sun_update > 86400:
        sunrise_time, sunset_time = get_sun_times()
        last_sun_update = time.time()
    if time.time() - last_weather_update > 1800 or previous_status is None:
        weather_main = get_weather_and_sun_times()
        last_weather_update = time.time()
    current_time_obj = datetime.strptime(current_time, "%H:%M").time()
    weather_emoji = get_weather_emoji(weather_main, current_time_obj, sunrise_time, sunset_time)
    status_message = f"{weather_emoji} | {current_time}"
    if status_message != previous_status:
        change_status(discord_token, status_message)
        print(f"Status updated to: {status_message}")
        previous_status = status_message
    time.sleep(1)
