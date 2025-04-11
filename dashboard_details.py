import pandas as pd
import datetime as dt
from datetime import datetime, timedelta
import os
import requests
from dotenv import load_dotenv
import csv
import sys
import matplotlib.pyplot as plt

# Optional custom exception
try:
    from src.exception.custom_exception import ProjectException
except ImportError:
    def ProjectException(e, sys):
        print("Exception:", e)

# Load API key
load_dotenv()
api_key = os.getenv("API_KEY")

class Dashboard:
    def load_data(self, location, days=1):
        api_key = "baadbd9843734bd78c074200250504"
        self.location = location
        print(self.location)
        try:
            #output_path = f"src/data_set/{location}_forecast_weather.csv"
            with open(f"src/data_set/{location}_forecast_weather.csv", "w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["DateTime", "Temperature (C)", "Temperature (F)", "Condition", "Humidity", "Wind (kph)", "Pressure (mb)"])

                url = f"http://api.weatherapi.com/v1/forecast.json?key={api_key}&q={location}&days={days}"
                response = requests.get(url)

                if response.status_code == 200:
                    data = response.json()
                    hourly_data = data['forecast']['forecastday'][0]['hour']

                    for hour in hourly_data:
                        writer.writerow([
                            hour['time'],
                            hour['temp_c'],
                            hour['temp_f'],
                            hour['condition']['text'],
                            hour['humidity'],
                            hour['wind_kph'],
                            hour['pressure_mb']
                        ])
                    print(f"✅ Weather data saved to ")
                else:
                    print(f"❌ Failed to fetch data: {response.status_code}")

        except Exception as e:
            print(f"⚠️ Error: {e}")
            ProjectException(e, sys)

    def get_data(self):
        try:
            path = f"src/data_set/{self.location}_forecast_weather.csv"
            self.forecast_data = pd.read_csv(path, encoding='latin1')
        except Exception as e:
            print(f"⚠️ Error loading CSV: {e}")
            ProjectException(e, sys)

    def featureEngineering(self):
        try:
            df = self.forecast_data.copy()
            df['DateTime'] = pd.to_datetime(df['DateTime'])
            df['Hour'] = df['DateTime'].dt.hour
            df['Feels_Muggy'] = ((df['Humidity'] > 65) & (df['Temperature (F)'] > 75)).astype(int)
            return df
        
        except Exception as e:
            print(f"⚠️ Feature Engineering Error: {e}")
            ProjectException(e, sys)
            return None
        
    def part_of_day_hour(self):
        try:
            df = self.featureEngineering()
            if df is None:
                return None, None, None, None
            df['DateTime'] = pd.to_datetime(df['DateTime'])
            df['Hour'] = df['DateTime'].dt.hour
            df['PartOfDay'] = df['DateTime'].dt.hour 
            
            return df
        except Exception as e:
            print(f"⚠️ Feature Engineering Error: {e}")
            ProjectException(e, sys)
            return None

    def part_of_day_temprature_avarage(self):
        df = self.featureEngineering()
        if df is None:
            return None, None, None, None
        # Morning: 5AM to 11AM
        morning_df = df[(df['Hour'] >= 5) & (df['Hour'] < 12)]['Temperature (C)'].mean()
        print(morning_df)
        # Afternoon: 12PM to 3PM
        afternoon_df = df[(df['Hour'] >= 12) & (df['Hour'] < 16)]['Temperature (C)'].mean()
        # Evening: 4PM to 7PM
        evening_df = df[(df['Hour'] >= 16) & (df['Hour'] < 20)]['Temperature (C)'].mean()
        # Night: 8PM to 4AM
        night_df = df[(df['Hour'] >= 20) | (df['Hour'] < 5)]['Temperature (C)'].mean()

        return (morning_df,afternoon_df,evening_df,night_df)
    
    def part_of_day_humidity_avarage(self):
        df = self.featureEngineering()
        if df is None:
            return None, None, None, None
        # Morning: 5AM to 11AM
        morning_df = df[(df['Hour'] >= 5) & (df['Hour'] < 12)]['Humidity'].mean()
        print(morning_df)
        # Afternoon: 12PM to 3PM
        afternoon_df = df[(df['Hour'] >= 12) & (df['Hour'] < 16)]['Humidity'].mean()
        # Evening: 4PM to 7PM
        evening_df = df[(df['Hour'] >= 16) & (df['Hour'] < 20)]['Humidity'].mean()
        # Night: 8PM to 4AM
        night_df = df[(df['Hour'] >= 20) | (df['Hour'] < 5)]['Humidity'].mean()

        return (morning_df,afternoon_df,evening_df,night_df)
    
    def call(self, location):
        self.load_data(location)
        self.get_data()
        return self.part_of_day_temprature_avarage()
