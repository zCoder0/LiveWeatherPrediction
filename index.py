import streamlit as st
import pandas as pd
import datetime as dt
import os
import requests
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from dashboard_details import Dashboard
from twilio.rest import Client
from streamlit_js_eval import streamlit_js_eval

# Load API Key
load_dotenv()
api_key = os.getenv("API_KEY")
api_key = "baadbd9843734bd78c074200250504"  # Replace with your real API key

# Streamlit Config
st.set_page_config(page_title="🌤️ Weather Dashboard", layout="centered")
st.title("🌦️ Live Weather Dashboard")
st.markdown("Live location enabled! Get weather update based on your GPS location.")

# JS-based GPS location fetch
coords = streamlit_js_eval(js_expressions="navigator.geolocation.getCurrentPosition((pos) => ({lat: pos.coords.latitude, lon: pos.coords.longitude}))", key="get_location")

# Get city name from GPS
def get_location_from_coords(lat, lon):
    try:
        res = requests.get(f"https://api.weatherapi.com/v1/current.json?key={api_key}&q={lat},{lon}")
        data = res.json()
        return data["location"]["name"], lat, lon
    except:
        return "Thanjavur", lat, lon  # fallback

if coords:
    city, lat, lon = get_location_from_coords(coords["lat"], coords["lon"])
    location_input = st.text_input("📍 Your Current Location", value=city)
else:
    location_input = st.text_input("📍 Your Location", value="Thanjavur")

# Load current weather
def load_current(location):
    url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={location}&aqi=yes"
    response = requests.get(url)
    if response.status_code == 200:
        weather_data = response.json()
        return weather_data['current'], weather_data['location']
    else:
        return None, None

# Send Message
def send_msg(condition):
    try:
        account_sid = "AC46555440f85435feecf54bc4f3640e65"
        auth_token = "37ae11a72e40a71356a2ecf04d"
        twilio_number = "+13075561605"
        to_number = "+918072620523"

        client = Client(account_sid, auth_token)
        if condition == "Rain":
            msg = "Hey bro, it's raining outside. Stay safe and carry an umbrella."
        elif condition == "Sunny":
            msg = "Hey bro, it's sunny outside. Enjoy the weather."
        else:
            msg = f"Current weather is: {condition}"

        message = client.messages.create(
            body=msg,
            from_=twilio_number,
            to=to_number
        )
        print("Message SID:", message.sid)
    except Exception as e:
        st.markdown(f"Error sending message : {e}")
        print(f"Error sending message: {e}")

# Send only once every hour
def should_send_message():
    current_time = dt.datetime.now()
    if "last_sent" not in st.session_state:
        st.session_state.last_sent = current_time
        return True
    elapsed = current_time - st.session_state.last_sent
    if elapsed.total_seconds() > 3600:  # 1 hour
        st.session_state.last_sent = current_time
        return True
    return False

# Weather UI
if location_input:
    current, location = load_current(location_input)
    if current:
        st.markdown(f"#### 📍 Location: {location['name']}, {location['region']}, {location['country']}")
        st.markdown(f"🕓 Local Time: `{location['localtime']}`")
        col1, col2, col3 = st.columns(3)
        col1.metric("🌡️ Temperature", f"{current['temp_c']}°C")
        col2.metric("💧 Humidity", f"{current['humidity']}%")
        col3.metric("🌬️ Wind", f"{current['wind_kph']} km/h")

        st.markdown("#### 🌤️ Condition")
        st.image(f"https:{current['condition']['icon']}", width=100)
        st.subheader(f"{current['condition']['text']}")

        #if should_send_message():
        #    send_msg(current['condition']['text'])
        send_msg(current['condition']['text'])
        # Dashboard visualizations
        db = Dashboard()
        morning_mean, afternoon_mean, evening_mean, night_mean = db.call(location_input)
        morning_mean_humidity, afternoon_mean_humidity, evening_mean_humidity, night_mean_humidity = db.part_of_day_humidity_avarage()

        labels = ['Morning', 'Afternoon', 'Evening', 'Night']
        temperatures = [morning_mean, afternoon_mean, evening_mean, night_mean]
        humidities = [morning_mean_humidity, afternoon_mean_humidity, evening_mean_humidity, night_mean_humidity]

        # Temperature Chart
        fig_temp, ax_temp = plt.subplots(figsize=(8, 5))
        ax_temp.bar(labels, temperatures, color=['#FFADAD', '#FFD6A5', '#B5EAD7', '#A0C4FF'])
        ax_temp.set_title("Temperature - Day Parts")
        st.pyplot(fig_temp)

        # Humidity Chart
        fig_hum, ax_hum = plt.subplots(figsize=(8, 5))
        ax_hum.bar(labels, humidities, color=['#CDB4DB', '#FFC6FF', '#A0C4FF', '#B9FBC0'])
        ax_hum.set_title("Humidity - Day Parts")
        st.pyplot(fig_hum)
    else:
        st.error("❌ Could not fetch weather data. Please check the location.")
