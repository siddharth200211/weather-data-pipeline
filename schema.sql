
CREATE DATABASE IF NOT EXISTS weather_db;

USE weather_db;

CREATE TABLE IF NOT EXISTS current_weather (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME NOT NULL,
    temperature FLOAT,
    humidity FLOAT,
    wind_speed FLOAT,
    UNIQUE KEY unique_weather_timestamp (timestamp)
);

CREATE TABLE IF NOT EXISTS cleaned_weather (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME NOT NULL,
    temperature FLOAT,
    humidity FLOAT,
    wind_speed FLOAT,
    weather_category VARCHAR(30),
    UNIQUE KEY unique_cleaned_timestamp (timestamp)
);
