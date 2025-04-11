import requests 
from dotenv import load_dotenv
import os
from src.exception.custom_exception import ProjectException
import sys
from datetime import datetime, timedelta
import csv
import pandas as pd

load_dotenv()
api_key = os.getenv('API_KEY')
api_key="baadbd9843734bd78c074200250504"

class DataIntegstion():
    def __init__(self):
        try:
            self.API_KEY = api_key
            self.start_date = datetime.strptime("2024-04-01", "%Y-%m-%d")
            self.end_date = datetime.strptime("2025-04-10", "%Y-%m-%d")
            
        except Exception as e:
            print(f"Error: {e}")
            ProjectException(e,sys)
    
    def load_data(self,location):
        try:
            self.location = location
            with open(f"src/data_set/{location}_1_year_weather.csv", "w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["DateTime", "Temperature (C)","Temperature (F)", "Condition", "Humidity", "Wind (kph)", "Pressure (mb)"])

                current_date = self.start_date
                while current_date <= self.end_date:
                    date_str = current_date.strftime("%Y-%m-%d")
                    print(f"Fetching data for {date_str}...")

                    url = f"http://api.weatherapi.com/v1/history.json?key={self.API_KEY}&q={location}&dt={date_str}"

                    response = requests.get(url)
                    if response.status_code == 200:
                        data = response.json()
                        hourly_data = data['forecast']['forecastday'][0]['hour']
                        for hour in hourly_data:
                            writer.writerow([
                                    date_str,
                                    hour['time'],
                                    hour['temp_c'],
                                    hour['temp_f'],
                                    hour['condition']['text'],
                                    hour['humidity'],
                                    hour['wind_kph'],
                                    hour['pressure_mb']
                            ])
                    else:
                        print(f"❌ Failed for {date_str}: {response.status_code}")
                        
                    current_date += timedelta(days=1)
            print(f"✅ One-year data saved to {location}_1_year_weather.csv")
        except Exception as e:
            print(f"⚠️ Error on {date_str}: {e}")
            ProjectException(e,sys)

    def get_data(self):
        try:
            path = os.path.join('src\data_set', os.listdir('src/data_set')[0])
            self.weather_data = pd.read_csv(path,encoding='latin1')
        except Exception as e:
            print(f"⚠️ Error on : {e}")
            ProjectException(e,sys)
        