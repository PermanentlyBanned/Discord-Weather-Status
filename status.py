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
        is_daytime = sunrise_time <= current_time <= sunset_time

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
    weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={weather_api_key}&units=metric"
    response = requests.get(weather_url)
    if response.status_code == 200:
        weather_data = response.json()
        try:
            weather_main = weather_data['weather'][0]['main']
            sunrise_timestamp = weather_data['sys']['sunrise']
            sunset_timestamp = weather_data['sys']['sunset']
            sunrise_time = datetime.fromtimestamp(sunrise_timestamp, local_tz).time()
            sunset_time = datetime.fromtimestamp(sunset_timestamp, local_tz).time()
            return weather_main, sunrise_time, sunset_time
        except (KeyError, ValueError) as e:
            print(f"Error parsing weather data: {e}")
    else:
        print(f"Weather API error: {response.status_code} - {response.text}")
    return "Clear", None, None

previous_status = None
last_weather_update = time.time()

while True:
    current_time = get_current_time()
    if time.time() - last_weather_update > 1800 or previous_status is None:
        weather_main, sunrise_time, sunset_time = get_weather_and_sun_times()
        last_weather_update = time.time()
    current_time_obj = datetime.strptime(current_time, "%H:%M").time()
    weather_emoji = get_weather_emoji(weather_main, current_time_obj, sunrise_time, sunset_time)
    status_message = f"{weather_emoji} | {current_time}"
    if status_message != previous_status:
        change_status(discord_token, status_message)
        print(f"Status updated to: {status_message}")
        previous_status = status_message
    time.sleep(1)
