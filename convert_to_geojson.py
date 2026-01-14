import requests
import json
import os
import pandas as pd
from datetime import datetime

# URL to fetch traffic flow data
base_url = "https://api.tomtom.com/traffic/services/4/flowSegmentData/relative0/10/json"
api_key = os.getenv('tomtom_key')

# Path to the CSV file in your GitHub repository
csv_url = "https://raw.githubusercontent.com/TaylorsvilleGIS/Traffic/refs/heads/main/road_midpoints.csv?token=GHSAT0AAAAAADTHUU43I6OQ6KAF4GVUFGG62LH67SQ"

# Read the CSV file
df = pd.read_csv(csv_url)

# Initialize GeoJSON structure
geojson = {
    "type": "FeatureCollection",
    "features": []
}

# Loop through each row in the CSV file
for index, row in df.iterrows():
    lat = row['Latitude']
    lon = row['Longitude']
    
    # Build the request URL
    url = f"{base_url}?point={lat},{lon}&unit=MPH&openLr=false&key={api_key}"
    
    response = requests.get(url)
    if response.status_code == 200:
        traffic_data = response.json()
        
        if "flowSegmentData" in traffic_data:
            segment = traffic_data["flowSegmentData"]
            coordinates = segment["coordinates"]["coordinate"]
            
            line_coordinates = [[coord["longitude"], coord["latitude"]] for coord in coordinates]

            last_updated = datetime.utcnow().isoformat() + 'Z'

            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": line_coordinates
                },
                "properties": {
                    "currentSpeed": segment["currentSpeed"],
                    "freeFlowSpeed": segment["freeFlowSpeed"],
                    "confidence": segment["confidence"],
                    "roadClosure": segment["roadClosure"],
                    "last_updated": last_updated
                }
            }
            geojson["features"].append(feature)

# Save the GeoJSON to a file
with open('traffic_data.geojson', 'w') as f:
    json.dump(geojson, f)

print("GeoJSON file created successfully.")
