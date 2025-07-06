import requests
import time
import os
import logging
import signal
import sys
from datetime import datetime
from pytz import timezone

log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, log_level),
    format='%(asctime)s - %(levelname)s - %(message)s'
)

discord_token = os.getenv("DISCORD_TOKEN")
weather_api_key = os.getenv("WEATHER_API_KEY")
latitude = os.getenv("LATITUDE")
longitude = os.getenv("LONGITUDE")
timezone_str = os.getenv("TIMEZONE", "Europe/Berlin")
status_message_format = os.getenv("STATUS_MESSAGE_FORMAT", "{weather_emoji} {current_time}")
update_interval = int(os.getenv("UPDATE_INTERVAL", "60"))
weather_update_interval = int(os.getenv("WEATHER_UPDATE_INTERVAL", "1800"))

if not all([discord_token, weather_api_key, latitude, longitude]):
    logging.error("Missing required environment variables: DISCORD_TOKEN, WEATHER_API_KEY, LATITUDE, LONGITUDE")
    sys.exit(1)

try:
    local_tz = timezone(timezone_str)
except Exception as e:
    logging.error(f"Invalid timezone '{timezone_str}': {e}")
    local_tz = timezone("Europe/Berlin")

def signal_handler(sig, frame):
    logging.info("Shutting down gracefully...")
    try:
        os.remove("/tmp/health")
    except FileNotFoundError:
        pass
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def create_health_check():
    try:
        with open("/tmp/health", "w") as f:
            f.write(str(time.time()))
    except Exception as e:
        logging.warning(f"Could not create health check file: {e}")

def change_status(token, message):
    headers = {'authorization': token}
    json_data = {"custom_status": {"text": message}}
    try:
        response = requests.patch(
            "https://discord.com/api/v10/users/@me/settings", 
            headers=headers, 
            json=json_data,
            timeout=10
        )
        response.raise_for_status()
        logging.info(f"Status updated to: {message}")
        return True
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to update status: {e}")
        return False

def get_current_time():
    return datetime.now(local_tz).strftime("%H:%M")

def should_show_temperature():
    now = datetime.now(local_tz)
    return 25 <= now.second <= 35

def wait_for_next_update():
    now = datetime.now(local_tz)
    current_second = now.second
    
    if current_second < 25:
        seconds_to_wait = 25 - current_second
    elif current_second <= 35:
        seconds_to_wait = 36 - current_second
    else:
        seconds_to_wait = 60 - current_second + 25
    
    time.sleep(seconds_to_wait)

def get_weather_emoji(weather_description, current_time, sunrise_time, sunset_time):
    weather_lower = weather_description.lower()
    
    is_day = sunrise_time <= current_time <= sunset_time if sunrise_time and sunset_time else True
    
    if "clear" in weather_lower or "sunny" in weather_lower:
        return "☀️" if is_day else "🌙"
    elif "partly cloudy" in weather_lower:
        return "⛅" if is_day else "☁️"
    elif "cloud" in weather_lower or "overcast" in weather_lower:
        return "☁️"
    elif "rain" in weather_lower or "drizzle" in weather_lower:
        return "🌧️"
    elif "thunderstorm" in weather_lower or "thunder" in weather_lower:
        return "⛈️"
    elif "snow" in weather_lower:
        return "❄️"
    elif "mist" in weather_lower or "fog" in weather_lower:
        return "🌫️"
    elif "hail" in weather_lower or "sleet" in weather_lower or "blizzard" in weather_lower:
        return "🌨️"
    elif "tornado" in weather_lower:
        return "🌪️"
    elif "hurricane" in weather_lower:
        return "🌀"
    elif "sand" in weather_lower or "dust" in weather_lower:
        return "🌪️"
    elif "smoke" in weather_lower:
        return "🌫️"
    else:
        return "☀️" if is_day else "🌙"

def get_weather_and_sun_times():
    weather_url = f"http://api.weatherapi.com/v1/forecast.json?key={weather_api_key}&q={latitude},{longitude}&days=1"
    try:
        response = requests.get(weather_url, timeout=10)
        response.raise_for_status()
        weather_data = response.json()
        
        weather_description = weather_data['current']['condition']['text']
        temperature = weather_data['current']['temp_c']
        
        sunrise_time = datetime.strptime(
            weather_data['forecast']['forecastday'][0]['astro']['sunrise'], 
            '%I:%M %p'
        ).time()
        sunset_time = datetime.strptime(
            weather_data['forecast']['forecastday'][0]['astro']['sunset'], 
            '%I:%M %p'
        ).time()
        
        logging.info(f"Weather: {weather_description}, {temperature}°C")
        return weather_description, sunrise_time, sunset_time, temperature
        
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to fetch weather data: {e}")
        return "unknown", None, None, None

def main():
    logging.info("Discord Weather Status starting...")
    logging.info(f"Update interval: {update_interval}s, Weather update interval: {weather_update_interval}s")
    
    previous_status = None
    last_weather_update = 0
    weather_description = "unknown"
    sunrise_time = None
    sunset_time = None
    temperature = None
    
    create_health_check()
    
    weather_description, sunrise_time, sunset_time, temperature = get_weather_and_sun_times()
    last_weather_update = time.time()
    
    
    while True:
        try:
            current_time = get_current_time()
            show_temp = should_show_temperature()
            
            if time.time() - last_weather_update > weather_update_interval:
                weather_description, sunrise_time, sunset_time, temperature = get_weather_and_sun_times()
                last_weather_update = time.time()
            
            current_time_obj = datetime.strptime(current_time, "%H:%M").time()
            weather_emoji = get_weather_emoji(weather_description, current_time_obj, sunrise_time, sunset_time)
            
            if show_temp and temperature is not None:
                display_text = f"{temperature}°C"
            else:
                display_text = current_time
            
            status_message = status_message_format.format(
                weather_emoji=weather_emoji,
                current_time=display_text,
                temperature=f"{temperature}°C" if temperature else "",
                weather=weather_description
            )
            
            if status_message != previous_status:
                if change_status(discord_token, status_message):
                    previous_status = status_message
            
            create_health_check()
            
            wait_for_next_update()
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            time.sleep(30)

if __name__ == "__main__":
    main()
