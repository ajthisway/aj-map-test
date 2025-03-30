import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import json

FEED_URL = "https://share.garmin.com/Feed/Share/ajthisway"
OUTPUT_FILE = "test_map.geojson"

response = requests.get(FEED_URL)
response.raise_for_status()

root = ET.fromstring(response.text)
namespace = {'atom': 'http://www.w3.org/2005/Atom'}

points = []

for entry in root.findall('atom:entry', namespace):
    title = entry.find('atom:title', namespace).text
    updated = entry.find('atom:updated', namespace).text

    try:
        lat_lon = title.replace("Lat: ", "").replace(" Lon: ", ",").split(",")
        lat = float(lat_lon[0])
        lon = float(lat_lon[1])
        timestamp = datetime.strptime(updated, "%Y-%m-%dT%H:%M:%SZ")

        points.append({
            "lat": lat,
            "lon": lon,
            "timestamp": timestamp.isoformat()
        })
    except Exception as e:
        print(f"Skipping invalid entry: {title} ({e})")

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
