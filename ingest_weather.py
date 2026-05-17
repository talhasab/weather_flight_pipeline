import requests
import time
from sqlalchemy import create_engine, text

# 1. THE ADDRESS: Telling Python where our Warehouse is
# Structure: postgresql://username:password@location:port/database_name
DATABASE_URL = "postgresql://talha_admin:engineer_pass@localhost:5432/weather_flights"

# 2. THE PIPE: Creating a connection "engine"
engine = create_engine(DATABASE_URL)

def get_weather_data(city):
    """Goes to the internet and grabs raw weather data."""
    print(f"--- Step 1: Fetching weather for {city} ---")
    
    # We use a free 'mock' weather API that returns JSON (computer-readable text)
    url = f"https://wttr.in/{city}?format=j1"
    response = requests.get(url)
    
    # Convert the long web response into a Python 'Dictionary' (a labeled list)
    data = response.json()
    
    # Picking out just the 'items' we want
    current = data['current_condition'][0]
    
    clean_data = {
        "city": city,
        "temp": float(current['temp_C']),
        "humidity": int(current['humidity']),
        "desc": current['weatherDesc'][0]['value']
    }
    return clean_data

def load_to_database(weather_info):
    """Takes our clean list and parks it in the Postgres Warehouse."""
    print(f"--- Step 2: Saving {weather_info['city']} data to Postgres ---")
    
    # This is the SQL command (The 'Insert' verb)
    query = text("""
        INSERT INTO raw_weather_data (city_name, temperature, humidity, weather_description)
        VALUES (:city, :temp, :humidity, :desc)
    """)
    
    # Open the connection, do the work, and close it automatically
    with engine.connect() as connection:
        connection.execute(query, weather_info)
        connection.commit() # This 'locks' the data into the shelf
    
    print("Success! Data is now in the database.")

# --- THE EXECUTION ---
# This is where the worker actually starts their shift
if __name__ == "__main__":
    print("Starting the Continuous Ingestion Worker... (Press Ctrl+C to stop)")
    
    while True:
        try:
            my_report = get_weather_data("London")
            load_to_database(my_report)
            
            print("Worker taking a nap for 60 seconds...")
            time.sleep(60) # Wait for 1 minute
            
        except Exception as e:
            print(f"Oops! The truck crashed: {e}")
            time.sleep(10) # Wait a bit before trying again

