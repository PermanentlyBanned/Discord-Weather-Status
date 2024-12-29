import requests, time, os, logging
from datetime import datetime
from pytz import timezone

logging.basicConfig(level=logging.INFO)

discord_token = os.getenv("DISCORD_TOKEN")
weather_api_key = os.getenv("WEATHER_API_KEY")
latitude = os.getenv("LATITUDE")
longitude = os.getenv("LONGITUDE")
local_tz = timezone("Europe/Berlin")
status_message_format = os.getenv("STATUS_MESSAGE_FORMAT")

def change_status(token, message):
    headers = {'authorization': token}
    json_data = {"custom_status": {"text": message}}
    try:
        response = requests.patch("https://discord.com/api/v10/users/@me/settings", headers=headers, json=json_data)
        response.raise_for_status()
        logging.info(f"Status updated to: {message}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to update status: {e}")

def get_current_time():
    return datetime.now(local_tz).strftime("%H:%M")

def get_weather_emoji(weather_description, current_time, sunrise_time, sunset_time):
    if "clear" in weather_description or "sunny" in weather_description:
        return "☀️" if sunrise_time <= current_time <= sunset_time else "🌙"
    elif "cloud" in weather_description or "overcast" in weather_description:
        return "☁️"
    elif "rain" in weather_description or "drizzle" in weather_description:
        return "🌧️"
    elif "thunderstorm" in weather_description:
        return "⛈️"
    elif "snow" in weather_description:
        return "❄️"
    elif "mist" in weather_description or "fog" in weather_description:
        return "🌫️"
    elif "hail" in weather_description or "sleet" in weather_description or "blizzard" in weather_description:
        return "🌨️"
    elif "tornado" in weather_description:
        return "🌪️"
    elif "hurricane" in weather_description:
        return "🌀"
    elif "sand" in weather_description or "dust" in weather_description:
        return "🌪️"
    elif "smoke" in weather_description:
        return "🌫️"
    else:
        return "☀️" if sunrise_time <= current_time <= sunset_time else "🌙"

def get_weather_and_sun_times():
    weather_url = f"http://api.weatherapi.com/v1/forecast.json?key={weather_api_key}&q={latitude},{longitude}&days=1"
    try:
        response = requests.get(weather_url)
        response.raise_for_status()
        weather_data = response.json()
        weather_description = weather_data['current']['condition']['text'].lower()
        sunrise_time = datetime.strptime(weather_data['forecast']['forecastday'][0]['astro']['sunrise'], '%I:%M %p').time()
        sunset_time = datetime.strptime(weather_data['forecast']['forecastday'][0]['astro']['sunset'], '%I:%M %p').time()
        return weather_description, sunrise_time, sunset_time
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to fetch weather data: {e}")
        return "unknown", None, None

previous_time, previous_weather_emoji, last_weather_update = None, None, time.time()

while True:
    current_time = get_current_time()
    if time.time() - last_weather_update > 1800 or previous_weather_emoji is None:
        weather_description, sunrise_time, sunset_time = get_weather_and_sun_times()
        last_weather_update = time.time()
    current_time_obj = datetime.strptime(current_time, "%H:%M").time()
    weather_emoji = get_weather_emoji(weather_description, current_time_obj, sunrise_time, sunset_time)
    status_message = status_message_format.format(weather_emoji=weather_emoji, current_time=current_time)
    if status_message != previous_time:
        change_status(discord_token, status_message)
        previous_time = status_message
    time.sleep(1)
