import os
import requests
import csv
from dotenv import load_dotenv
from datetime import datetime


def fetch_weather(api_key: str, city="Moscow") -> dict:
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response = requests.get(url)
    weather_data = response.json()
    return weather_data


def write_to_csv(weather_data, city, filename='weather.csv'):
    dt = datetime.utcfromtimestamp(weather_data['dt']).strftime('%Y-%m-%d %H:%M:%S')
    weather_main = weather_data['weather'][0]['main']
    weather_description = weather_data['weather'][0]['description']
    temp = weather_data['main']['temp']
    feels_like = weather_data['main']['feels_like']
    pressure = weather_data['main']['pressure']
    wind_speed = weather_data['wind']['speed']

    data_row = [dt, city, weather_main, weather_description, temp, feels_like, pressure, wind_speed]

    with open(filename, mode='a', newline='\n') as file:
        writer = csv.writer(file)
        writer.writerow(data_row)


def fetch_and_write():
    load_dotenv(".env")
    api_key = os.getenv("API_KEY")
    city = "Moscow"
    data = fetch_weather(api_key=api_key, city=city)
    write_to_csv(data, city)


# if __name__ == "__main__":
#     # test weather API
#     load_dotenv(".env")
#     api_key = os.getenv("API_KEY")
#     city = "Moscow"
#     data = fetch_weather(api_key=api_key, city=city)
#     print(data)
#     write_to_csv(data, city)
