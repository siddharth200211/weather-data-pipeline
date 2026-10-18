
import requests
import pandas as pd
import mysql.connector
import matplotlib.pyplot as plt
from pathlib import Path
import os 


# ==========================================
# 1. EXTRACT: Fetch data from the API
# ==========================================

def extract_data():
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": 18.5204,
        "longitude": 73.8567,
        "current": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "wind_speed_10m"
        ),
        "timezone": "Asia/Kolkata"
    }

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()

    data = response.json()
    current = data["current"]

    print("Current Weather:")
    print(current)

    df = pd.DataFrame([{
        "timestamp": current["time"],
        "temperature": current["temperature_2m"],
        "humidity": current["relative_humidity_2m"],
        "wind_speed": current["wind_speed_10m"]
    }])

    return df


# ==========================================
# 2. DATABASE CONNECTION
# ==========================================

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user=os.getenv("MYSQL_HOST_USER", "root"),
        password=os.environ["MYSQL_PASSWORD"],
        database="weather_db"
    )


# ==========================================
# 3. LOAD: Store raw data in MySQL
# ==========================================

def load_raw_data(df):
    connection = get_connection()

    query = """
    INSERT INTO current_weather
    (timestamp, temperature, humidity, wind_speed)
    VALUES (%s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        temperature = VALUES(temperature),
        humidity = VALUES(humidity),
        wind_speed = VALUES(wind_speed)
    """

    cursor = connection.cursor()

    try:
        for row in df.itertuples(index=False):
            values = (
                row.timestamp,
                float(row.temperature),
                float(row.humidity),
                float(row.wind_speed)
            )
            cursor.execute(query, values)

        connection.commit()
        print("Raw data loaded into MySQL successfully!")

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()


# ==========================================
# 4. TRANSFORM: Clean data using Pandas
# ==========================================

def transform_data(df):
    df = df.copy()

    df["timestamp"] = pd.to_datetime(
        df["timestamp"], errors="coerce"
    )

    numeric_columns = [
        "temperature",
        "humidity",
        "wind_speed"
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column], errors="coerce"
        )

    df = df.drop_duplicates(subset=["timestamp"])

    df = df.dropna(
        subset=["timestamp"] + numeric_columns
    )

    # Validate values before transformation
    df = df[
        df["humidity"].between(0, 100)
        & (df["wind_speed"] >= 0)
    ].copy()

    for column in numeric_columns:
        df[column] = df[column].round(2)

    # Create a derived column
    df["weather_category"] = df["temperature"].apply(
        lambda temp: (
            "Hot" if temp >= 30
            else "Moderate" if temp >= 20
            else "Cool"
        )
    )

    return df


# ==========================================
# 5. LOAD: Store transformed data in MySQL
# ==========================================

def load_cleaned_data(df):
    connection = get_connection()

    query = """
    INSERT INTO cleaned_weather
    (timestamp, temperature, humidity, wind_speed,
     weather_category)
    VALUES (%s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        temperature = VALUES(temperature),
        humidity = VALUES(humidity),
        wind_speed = VALUES(wind_speed),
        weather_category = VALUES(weather_category)
    """

    cursor = connection.cursor()

    try:
        for row in df.itertuples(index=False):
            values = (
                row.timestamp.to_pydatetime(),
                float(row.temperature),
                float(row.humidity),
                float(row.wind_speed),
                row.weather_category
            )
            cursor.execute(query, values)

        connection.commit()
        print("Cleaned data loaded into MySQL successfully!")

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()


# ==========================================
# 6. REPORT: Query MySQL and generate outputs
# ==========================================

def generate_report():
    connection = get_connection()

    try:
        df = pd.read_sql(
            """
            SELECT timestamp, temperature, humidity,
                   wind_speed, weather_category
            FROM cleaned_weather
            ORDER BY timestamp
            """,
            connection
        )
    finally:
        connection.close()

    if df.empty:
        print("No cleaned data available for reporting.")
        return

    print("\n===== WEATHER REPORT =====")
    print(df.to_string(index=False))

    print("\n===== SUMMARY =====")
    print(
        df[["temperature", "humidity", "wind_speed"]]
        .describe()
    )

    output_dir = Path("output")
    output_dir.mkdir(parents=True, exist_ok=True)

    df.to_csv(
        output_dir / "weather_report.csv",
        index=False
    )

    plt.figure(figsize=(10, 5))
    plt.plot(
        df["timestamp"],
        df["temperature"],
        marker="o"
    )
    plt.title("Recorded Temperature")
    plt.xlabel("Timestamp")
    plt.ylabel("Temperature (°C)")
    plt.xticks(rotation=45)
    plt.tight_layout()

    plt.savefig(output_dir / "weather_report.png")
    plt.close()

    print("\nCSV and chart saved in the output folder.")


# ==========================================
# 7. MAIN PIPELINE: Run all stages in order
# ==========================================

def main():
    raw_df = extract_data()

    load_raw_data(raw_df)

    cleaned_df = transform_data(raw_df)

    load_cleaned_data(cleaned_df)

    generate_report()


if __name__ == "__main__":
    main()
