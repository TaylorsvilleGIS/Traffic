import os
import json
import requests
import pandas as pd

# ----------------------------
# Config
# ----------------------------

TOMTOM_KEY = os.getenv("TOMTOM_KEY")

CSV_URL = "https://raw.githubusercontent.com/TaylorsvilleGIS/Traffic/main/road_midpoints.csv"
OUTPUT_FILE = "traffic_data.geojson"

# ----------------------------
# Validation
# ----------------------------



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

features = []

for idx, row in df.iterrows():
    lat = row["Latitude"]
    lon = row["Longitude"]

    url = (
        "https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json"
        f"?point={lat},{lon}&key={TOMTOM_KEY}"
    )

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        segment = data.get("flowSegmentData")
        if not segment:
            continue

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
                "currentSpeed": segment.get("currentSpeed"),
                "freeFlowSpeed": segment.get("freeFlowSpeed"),
                "confidence": segment.get("confidence")
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
