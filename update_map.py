import requests
import xml.etree.ElementTree as ET
import json

# Live feed URL
FEED_URL = "https://share.garmin.com/Feed/ShareLoader/ajthisway"
OUTPUT_FILE = "test_map.geojson"

# Fetch the live KML feed
response = requests.get(FEED_URL)
response.raise_for_status()

# Debug: Print the content of the feed to verify it is being fetched
print("Fetched KML Feed: ")
print(response.text[:500])  # Just print the first 500 characters to check the content

# Parse the KML data
root = ET.fromstring(response.content)
namespace = {'kml': 'http://www.opengis.net/kml/2.2'}

points = []

# Iterate through Placemark entries (this will grab the track data)
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

# Check how many points were fetched
print(f"Fetched {len(points)} points")

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

# Save GeoJSON to file
with open(OUTPUT_FILE, "w") as f:
    json.dump(geojson, f)

print(f"Saved {len(points)} points to {OUTPUT_FILE}")
