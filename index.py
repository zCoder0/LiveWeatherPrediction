import streamlit as st
import pandas as pd
import datetime as dt
import time
import os
import requests
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from dashboard_details import Dashboard
from twilio.rest import Client

# Load API Key
load_dotenv()
api_key = os.getenv("API_KEY")
api_key = "baadbd9843734bd78c074200250504"  # Replace with your API key

# Streamlit Page Config
st.set_page_config(page_title="🌤️ Weather Dashboard", layout="centered")

# Title & Description
st.title("🌦️ Live Weather Dashboard")
st.markdown("Enter a location to get the current weather update!")

# 🔍 Search Box for Location
location_input = st.text_input("📍 Enter Location", value="Thanjavur")

# Load current weather
def load_current(location):
    url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={location}&aqi=yes"
    response = requests.get(url)
    if response.status_code == 200:
        weather_data = response.json()
        return weather_data['current'], weather_data['location']
    else:
        return None, None

# Function to send SMS based on condition
def send_msg(condition):
    try:
        account_sid = "AC46555440f85435feecf54bc4f3640e65"
        auth_token = "37ae11a72e40a71356a2ec9af38ef04d"
        twilio_number = "+13075561605"  # Replace with your Twilio number
        to_number = "+918072620523"     # Your verified number

        client = Client(account_sid, auth_token)

        if condition == "Rain":
            message_body = "Hey bro, it's raining outside. Stay safe and carry an umbrella."
        elif condition == "Sunny":
            message_body = "Hey bro, it's sunny outside. Enjoy the weather."
        else:
            message_body = f"Hey bro, current weather condition: {condition}"

        message = client.messages.create(
            body=message_body,
            from_=twilio_number,
            to=to_number
        )
        print("Message SID:", message.sid)
    except Exception as e:
        st.markdown(f"Error message : {e}")
        print(f"Error sending message: {e}")

# Main UI
if location_input:
    current, location = load_current(location_input)

    if current:
        # Display location info
        st.markdown(f"#### 📍 Location: {location['name']}, {location['region']}, {location['country']}")
        st.markdown(f"🕓 Local Time: `{location['localtime']}`")

        # Show main metrics
        col1, col2, col3 = st.columns(3)
        col1.metric("🌡️ Temperature", f"{current['temp_c']}°C")
        col2.metric("💧 Humidity", f"{current['humidity']}%")
        col3.metric("🌬️ Wind", f"{current['wind_kph']} km/h")

        # Weather condition
        st.markdown("#### 🌤️ Condition")
        st.image(f"https:{current['condition']['icon']}", width=100)
        st.subheader(f"{current['condition']['text']}")

        # ✅ Send SMS once per hour
        current_time = time.time()
        if 'last_sent_time' not in st.session_state:
            st.session_state.last_sent_time = 0

        if current_time - st.session_state.last_sent_time >= 3600:
    
            send_msg(current['condition']['text'])
            st.session_state.last_sent_time = current_time
            st.markdown(f"Last send Time " {st.session_state.last_sent_time})

        # 📊 Dashboard logic
        db = Dashboard()
        morning_mean, afternoon_mean, evening_mean, night_mean = db.call(location_input)
        morning_mean_humidity, afternoon_mean_humidity, evening_mean_humidity, night_mean_humidity = db.part_of_day_humidity_avarage()

        labels = ['Morning', 'Afternoon', 'Evening', 'Night']
        temperatures = [morning_mean, afternoon_mean, evening_mean, night_mean]
        humidities = [morning_mean_humidity, afternoon_mean_humidity, evening_mean_humidity, night_mean_humidity]

        # 🌡️ Temperature Bar Chart
        fig_temp, ax_temp = plt.subplots(figsize=(8, 5))
        bars_temp = ax_temp.bar(labels, temperatures, color=['#FFADAD', '#FFD6A5', '#B5EAD7', '#A0C4FF'])
        for bar in bars_temp:
            yval = bar.get_height()
            ax_temp.text(bar.get_x() + bar.get_width()/2, yval + 0.2, f"{yval:.2f}°C", ha='center', va='bottom')
        ax_temp.set_title("Temperature for Different Parts of the Day")
        ax_temp.set_xlabel(f"Part of Day - {location['name']}")
        ax_temp.set_ylabel("Temperature (°C)")
        ax_temp.set_ylim(0, max(temperatures) + 5)
        ax_temp.grid(axis='y', linestyle='--', alpha=0.5)
        st.markdown("## 📊 Average Temperature Trend by Part of the Day")
        st.pyplot(fig_temp)

        # 💧 Humidity Bar Chart
        fig_humidity, ax_hum = plt.subplots(figsize=(8, 5))
        bars_humidity = ax_hum.bar(labels, humidities, color=['#CDB4DB', '#FFC6FF', '#A0C4FF', '#B9FBC0'])
        for bar in bars_humidity:
            yval = bar.get_height()
            ax_hum.text(bar.get_x() + bar.get_width()/2, yval + 0.2, f"{yval:.2f}%", ha='center', va='bottom')
        ax_hum.set_title("Humidity for Different Parts of the Day")
        ax_hum.set_xlabel(f"Part of Day - {location['name']}")
        ax_hum.set_ylabel("Humidity (%)")
        ax_hum.set_ylim(0, max(humidities) + 5)
        ax_hum.grid(axis='y', linestyle='--', alpha=0.5)
        st.markdown("## 📊 Average Humidity Trend by Part of the Day")
        st.pyplot(fig_humidity)

    else:
        st.error("❌ Could not fetch weather data. Please check the location name.")
