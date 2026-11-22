"""fetch_data.py - CST1510 CW2
Gets earthquake data from the USGS API and saves it to DATA/raw.csv

Four small functions:
    get_data      -> ask the API (returns JSON, or None if it failed)
    make_table    -> records to a table (DataFrame)
    tidy_data     -> rename, keep, drop
    save_data     -> write the table to DATA/raw.csv
"""

import os
from datetime import date, timedelta

import requests
import pandas as pd

# ---------------------------------------------------------------
# SETTINGS - change these to your own (Steps 1 to 5)
# ---------------------------------------------------------------

# Steps 1/2: API address and parameters
URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"
PARAMS = {
    "format": "geojson",                                           # ask for JSON
    "starttime": (date.today() - timedelta(days=30)).isoformat(),  # last 30 days
    "endtime": date.today().isoformat(),
    "minmagnitude": 4.0,                                           # ignore tiny quakes
    "limit": 1000,                                                 # max rows to fetch
    "orderby": "time",
}

# Steps 3/4: the GeoJSON keeps the list of earthquakes under "features"
RECORDS_KEY = "features"

# Step 5: tidy up the table
RENAME = {
    "properties.mag": "magnitude",
    "properties.place": "place",
    "properties.time": "time",
    "properties.type": "type",
    "properties.tsunami": "tsunami",
    "properties.sig": "significance",
    "properties.felt": "felt_reports",
    "properties.alert": "alert",
    "properties.status": "status",
    "id": "event_id",
}
KEEP = [
    "event_id", "time", "place", "magnitude", "longitude", "latitude",
    "depth_km", "type", "tsunami", "significance", "felt_reports",
    "alert", "status",
]
DROP = []   # anything else you want removed, e.g. ["status"]

OUTPUT_PATH = os.path.join("DATA", "raw.csv")


# ---------------------------------------------------------------
# FUNCTIONS
# ---------------------------------------------------------------

def get_data(url, params):
    """Step 2: ask the API. Returns the JSON, or None if it failed."""
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as error:
        print(f"Could not get data from the API: {error}")
        return None
    except ValueError:
        print("The API did not return valid JSON.")
        return None


def make_table(data, records_key):
    """Steps 3 and 4: records to a table."""
    if data is None:
        return None

    records = data[records_key] if records_key else data
    df = pd.json_normalize(records)

    # USGS stores location as a list: [longitude, latitude, depth_km]
    if "geometry.coordinates" in df.columns:
        coords = pd.DataFrame(
            df["geometry.coordinates"].tolist(),
            columns=["longitude", "latitude", "depth_km"],
        )
        df = pd.concat([df.drop(columns=["geometry.coordinates"]), coords], axis=1)

    return df


def tidy_data(df):
    """Step 5: rename, keep, drop."""
    if df is None:
        return None

    df = df.rename(columns=RENAME)

    # time arrives as milliseconds since 1970 -> make it a real date/time
    if "time" in df.columns:
        df["time"] = pd.to_datetime(df["time"], unit="ms")

    if KEEP:
        df = df[[col for col in KEEP if col in df.columns]]
    if DROP:
        df = df.drop(columns=[col for col in DROP if col in df.columns])

    return df


def save_data(df, path):
    """Write the table to a CSV file (creates the folder if needed)."""
    if df is None:
        print("Nothing to save.")
        return

    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)

    df.to_csv(path, index=False)
    print(f"Saved {len(df)} rows to {path}")


# ---------------------------------------------------------------
# RUN
# ---------------------------------------------------------------

if __name__ == "__main__":
    data = get_data(URL, PARAMS)
    table = make_table(data, RECORDS_KEY)
    table = tidy_data(table)
    save_data(table, OUTPUT_PATH)