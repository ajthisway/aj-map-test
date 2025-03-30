import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import json

# KML feed URL (same link)
FEED_URL = "https://share.garmin.com/Feed/Share/ajthisway"
OUTPUT_FILE = "test_map.geojson"

# Fetch the KML feed
response = requests.get(FEED_URL)
response.raise_for_status()

root = ET.fromstring(response.text)
namespace = {
    'kml': 'http://www.opengis.net/kml/2.2'
}

points = []

for placemark in root.findall('.//kml:Placemark', namespace):
    try:
        coords = placemark.find('.//kml:Point/kml:coordinates', namespace).text.strip()
        lon, lat, *_ = map(float, coords.split(','))

        timestamp_elem = placemark.find('.//kml:TimeStamp/kml:when', namespace)
        timestamp = timestamp_elem.text if timestamp_elem is not None else None

        points.append({
            "lat": lat,
            "lon": lon,
            "timestamp": timestamp
        })
    except Exception as e:
        print(f"Skipping bad placemark: {e}")

# Build GeoJSON
geojson = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [p["lon"], p["lat"]]
            },
            "properties": {
                "timestamp": p["timestamp"]
            }
        } for p in points
    ]
}

with open(OUTPUT_FILE, "w") as f:
    json.dump(geojson, f)

print(f"Saved {len(points)} points to {OUTPUT_FILE}")
