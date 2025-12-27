import tkinter as tk
from tkinter import messagebox
import requests
from datetime import datetime
from PIL import Image, ImageTk
from io import BytesIO
import threading

# --- CONFIGURATION ---
OPENWEATHER_API_KEY = "07ed8b0c7da63359ba5059138c3a7293"

# --- FUNCTIONS ---
def get_weather(city):
    """Fetch current weather for a city."""
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
        response = requests.get(url)
        data = response.json()
        if data.get("cod") != 200:
            return None
        return data
    except Exception as e:
        messagebox.showerror("Error", f"Weather API error: {e}")
        return None

def get_forecast(lat, lon):
    """Fetch 7-day forecast using lat/lon."""
    try:
        url = f"https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&exclude=minutely,hourly,alerts&units=metric&appid={OPENWEATHER_API_KEY}"
        response = requests.get(url)
        data = response.json()
        if 'daily' in data:
            return data['daily'][:7]
        else:
            print("Forecast data not available.")
            return []
    except Exception as e:
        print(f"Forecast API error: {e}")
        return []

def get_quote():
    """Fetch a random positive quote."""
    try:
        res = requests.get("https://zenquotes.io/api/random")
        data = res.json()[0]
        return f"\"{data['q']}\" - {data['a']}"
    except Exception as e:
        return "Stay positive!"

def fetch_icon(icon_code):
    """Fetch weather icon from OpenWeather."""
    try:
        url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"
        response = requests.get(url)
        img_data = response.content
        img = Image.open(BytesIO(img_data))
        return ImageTk.PhotoImage(img)
    except:
        return None

def update_data():
    city = city_entry.get()
    weather_label.config(text="Loading weather...")
    quote_label.config(text="Loading quote...")
    forecast_frame.destroy()
    create_forecast_frame()

    def fetch():
        weather = get_weather(city)
        quote = get_quote()
        if weather:
            desc = weather['weather'][0]['description'].capitalize()
            temp = weather['main']['temp']
            feels = weather['main']['feels_like']
            weather_text = f"{city} Weather: {desc}\nTemp: {temp}°C, Feels like: {feels}°C"
            weather_label.config(text=weather_text)

            # Weather icon
            icon_code = weather['weather'][0]['icon']
            icon_img = fetch_icon(icon_code)
            if icon_img:
                icon_label.config(image=icon_img)
                icon_label.image = icon_img

            # Forecast
            forecast_data = get_forecast(weather['coord']['lat'], weather['coord']['lon'])
            for i, day in enumerate(forecast_data):
                date = datetime.fromtimestamp(day['dt']).strftime('%a %d %b')
                desc = day['weather'][0]['main']
                temp_day = round(day['temp']['day'])
                icon_code = day['weather'][0]['icon']
                icon_img = fetch_icon(icon_code)

                day_frame = tk.Frame(forecast_frame, bg="#fffbf0", bd=1, relief="solid", padx=5, pady=5)
                day_frame.grid(row=0, column=i, padx=5)
                tk.Label(day_frame, text=date, bg="#fffbf0", font=("Helvetica",10,"bold")).pack()
                if icon_img:
                    lbl = tk.Label(day_frame, image=icon_img, bg="#fffbf0")
                    lbl.image = icon_img
                    lbl.pack()
                tk.Label(day_frame, text=f"{desc}\n{temp_day}°C", bg="#fffbf0").pack()
        else:
            weather_label.config(text="City not found!")
        quote_label.config(text=quote)
        time_label.config(text=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    threading.Thread(target=fetch).start()

def update_time():
    """Update date & time every second."""
    time_label.config(text=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    root.after(1000, update_time)

def create_forecast_frame():
    """Create a frame for 7-day forecast cards."""
    global forecast_frame
    forecast_frame = tk.Frame(root, bg="#f0f0f0")
    forecast_frame.pack(pady=10)

# --- GUI SETUP ---
root = tk.Tk()
root.title("Advanced Weather & Positivity App")
root.geometry("900x600")
root.config(bg="#a0c4ff")

# Title
title_label = tk.Label(root, text="Advanced Weather & Positivity App", font=("Helvetica", 20, "bold"), bg="#a0c4ff")
title_label.pack(pady=10)

# Date & Time
time_label = tk.Label(root, text="", font=("Helvetica", 14), bg="#a0c4ff")
time_label.pack()
update_time()

# City input and refresh button
city_frame = tk.Frame(root, bg="#a0c4ff")
city_frame.pack(pady=10)
city_entry = tk.Entry(city_frame, font=("Helvetica", 14), width=30)
city_entry.pack(side="left", padx=5)
city_entry.insert(0, "London")
refresh_button = tk.Button(city_frame, text="Get Weather & Quote", font=("Helvetica", 12, "bold"), bg="#ffd6a5", command=update_data)
refresh_button.pack(side="left", padx=5)

# Weather info
weather_label = tk.Label(root, text="", font=("Helvetica", 14), bg="#caffbf", wraplength=450)
weather_label.pack(pady=10)

# Weather icon
icon_label = tk.Label(root, bg="#caffbf")
icon_label.pack()

# Positive Quote
quote_label = tk.Label(root, text="", font=("Helvetica", 12, "italic"), bg="#fdffb6", wraplength=800, justify="center")
quote_label.pack(pady=10)

# Forecast frame
create_forecast_frame()

# Initialize
update_data()
root.mainloop()