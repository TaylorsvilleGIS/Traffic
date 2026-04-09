import os
import json
import requests
import pandas as pd
from datetime import datetime 
from ZoneInfo import ZoneInfo

# ----------------------------
# Config
# ----------------------------

tomtom_key = os.getenv("tomtom_key")

CSV_URL = "https://raw.githubusercontent.com/TaylorsvilleGIS/Traffic/refs/heads/main/traffic_probes.csv"
OUTPUT_FILE = "traffic_data.geojson"

# ----------------------------
# Validation
# ----------------------------

if not tomtom_key:
    print("ERROR: tomtom_key environment variable not set")
    exit(1)

# ----------------------------
# Load CSV
# ----------------------------

print("Reading CSV...")
df = pd.read_csv(CSV_URL)
print("CSV rows:", len(df))

# Expecting columns named 'Latitude' and 'Longitude'
if not {"Latitude", "Longitude"}.issubset(df.columns):
    print("ERROR: CSV missing Latitude/Longitude columns")
    exit(1)

# ----------------------------
# Build GeoJSON Features
# ----------------------------

#-----------------------------
# TimeStamp
#-----------------------------
updated_at = datetime.now(ZoneInfo("America/Denver")).strftime("%m/%d/%Y %I:%M %p")

features = []

for idx, row in df.iterrows():
    lat = row["Latitude"]
    lon = row["Longitude"]

    url = (
        "https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json"
        f"?point={lat},{lon}&key={tomtom_key}"
    )

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        segment = data.get("flowSegmentData")
        if not segment:
            continue

        current_speed = segment.get("currentSpeed")
        free_flow_speed = segment.get("freeFlowSpeed")

        # Avoid divide-by-zero and missing values
        if current_speed is not None and free_flow_speed not in (None, 0):
            speed_ratio = round(current_speed / free_flow_speed, 2)
        else:
            speed_ratio = None

        coordinates = segment["coordinates"]["coordinate"]

        line = [
            [coord["longitude"], coord["latitude"]]
            for coord in coordinates
        ]

        feature = {
            "type": "Feature",
            "geometry": {
                "type": "LineString",
                "coordinates": line
            },
            "properties": {
                "currentSpeed": current_speed,
                "freeFlowSpeed": free_flow_speed,
                "confidence": segment.get("confidence"),
                "speed_ratio": speed_ratio,
                "updatedAt": updated_at
            }
        }

        features.append(feature)

    except Exception as e:
        print(f"TomTom error at row {idx}: {e}")
        continue

print("Features created:", len(features))

# ----------------------------
# SAFETY GUARD (CRITICAL)
# ----------------------------

if len(features) == 0:
    print("No features created — existing GeoJSON will be preserved")
    exit(0)

# ----------------------------
# Write GeoJSON
# ----------------------------

geojson = {
    "type": "FeatureCollection",
    "features": features
}

with open(OUTPUT_FILE, "w") as f:
    json.dump(geojson, f)

print("GeoJSON written successfully:", OUTPUT_FILE)
