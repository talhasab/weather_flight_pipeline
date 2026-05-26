import requests
import time
import os
from sqlalchemy import create_engine, text, inspect

# --- CONFIGURATION ---
# This is the "Settings" section of our worker
TARGET_CITY = "London"
SLEEP_TIME = 60 # Seconds between updates

# THE ADDRESS: We check the system for a label named 'DB_HOST'.
# 1. If we find it (Inside Docker), we use that value (postgres_warehouse).
# 2. If we don't (On your Laptop), we default to '127.0.0.1'.
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DATABASE_URL = f"postgresql://data_engineer:password123@{DB_HOST}:5432/weather_data"

# THE PIPE: Creating a connection "engine"
engine = create_engine(DATABASE_URL)

def ensure_table_exists():
    """
    IDEMPOTENCY CHECK:
    This function checks the database to see if our 'filling cabinet' (table) 
    exists. If it's missing, it builds it. This allows us to restart the 
    script safely without crashing.
    """
    print("--- Checking for raw_weather_data table ---")
    with engine.connect() as connection:
        inspector = inspect(connection)
        if not inspector.has_table("raw_weather_data"):
            print("Table raw_weather_data not found. Creating it...")
            create_table_query = text("""
                CREATE TABLE raw_weather_data (
                    id SERIAL PRIMARY KEY,
                    city_name VARCHAR(255) NOT NULL,
                    temperature FLOAT NOT NULL,
                    humidity INTEGER NOT NULL,
                    weather_description VARCHAR(255) NOT NULL,
                    ingestion_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            connection.execute(create_table_query)
            connection.commit()
            print("Table raw_weather_data created successfully.")
        else:
            print("Table raw_weather_data already exists.")

def get_weather_data(city):
    """
    EXTRACTION:
    Connects to the wttr.in API, fetches raw JSON data, and 
    transforms it into a clean Python dictionary containing 
    only the temperature, humidity, and description.
    """
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
    
    print(f"Success! {weather_info['city']} weather recorded at {weather_info['temp']}°C.")

# --- THE EXECUTION ---
# This is where the worker actually starts their shift
if __name__ == "__main__":
    print("Starting the Continuous Ingestion Worker... (Press Ctrl+C to stop)")
    ensure_table_exists() # Ensure table exists before starting ingestion
    
    while True:
        try:
            my_report = get_weather_data(TARGET_CITY)
            load_to_database(my_report)
            
            print(f"Worker taking a nap for {SLEEP_TIME} seconds...")
            time.sleep(SLEEP_TIME) 
            
        except Exception as e:
            print(f"Oops! The truck crashed: {e}")
            time.sleep(10) # Wait a bit before trying again
