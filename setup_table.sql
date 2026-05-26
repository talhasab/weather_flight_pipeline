-- This script creates our initial weather table
CREATE TABLE IF NOT EXISTS raw_weather_data (
    id SERIAL PRIMARY KEY,
    city_name VARCHAR(255) NOT NULL,
    temperature FLOAT NOT NULL,
    humidity INTEGER NOT NULL,
    weather_description VARCHAR(255) NOT NULL,
    ingestion_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);