# Weather Data Pipeline

## Overview
A beginner-friendly Data Engineering project that extracts current weather data from the Open-Meteo API, loads raw data into MySQL, transforms the data using Pandas, and generates reports.

## Architecture
Open-Meteo API → Python → Raw MySQL Table → Pandas Transformation → Cleaned MySQL Table → CSV and Chart

## Tech Stack
- Python
- REST API
- Pandas
- MySQL
- SQL
- Matplotlib
- Git and GitHub

## Pipeline Stages
1. **Extract:** Fetch current weather data from Open-Meteo.
2. **Load:** Store the raw observation in MySQL.
3. **Transform:** Validate values, handle missing data, remove duplicates, and derive a weather category.
4. **Load:** Store transformed data in a separate MySQL table.
5. **Report:** Query the cleaned data, export a CSV, and generate a temperature chart.

## Project Structure
- `main.py` — Pipeline logic
- `requirements.txt` — Python dependencies
- `.gitignore` — Files excluded from version control
- `schema.sql` — Database table definitions
- `output/` — Generated reports

## Setup
1. Install Python and MySQL.
2. Install dependencies using `python -m pip install -r requirements.txt`.
3. Create the `weather_db` database and tables using `schema.sql`.
4. Configure the `MYSQL_PASSWORD` environment variable.
5. Run `python main.py`.

## Future Improvements
- Schedule automatic pipeline execution.
- Add logging and automated tests.
- Add historical weather data.
- Orchestrate the pipeline with Apache Airflow.
