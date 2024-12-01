from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import geopy.distance
import os
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

# Enable CORS for all domains
CORS(app)

# Open AQ API Key
API_KEY = os.environ['OPENAQ_API_KEY']
# Function to calculate the distance between two coordinates
def find_closest_coordinates(user_lat, user_lon, results):
    closest_distance = float('inf')
    closest_coordinates = None

    for result in results:
        lat = result['coordinates']['latitude']
        lon = result['coordinates']['longitude']
        
        # Calculate distance between user coordinates and each result
        dist = geopy.distance.distance((user_lat, user_lon), (lat, lon)).km
        
        if dist < closest_distance:
            closest_distance = dist
            closest_coordinates = result['coordinates']
            locationid = result['id']
    
    return closest_coordinates, closest_distance, locationid

@app.route("/get-closest-coordinates", methods=["GET"])
def get_locations_by_coordinates():
    user_lat = float(request.args.get('latitude'))  # Get latitude from query params
    user_lon = float(request.args.get('longitude'))  # Get longitude from query params
    radius = 10000
    limit = 100

    try:
        if not (-90 <= user_lat <= 90 and -180 <= user_lon <= 180):
            return jsonify({"error": "Coordinates out of range"}), 400

    except ValueError:
        return jsonify({"error": "Invalid format for coordinates"}), 400

    # Construct API URL
    api_url = (
        f"https://api.openaq.org/v3/locations?coordinates={user_lat},{user_lon}"
        f"&radius={radius}&limit={limit}"
    )
    headers = {"X-API-Key": API_KEY}

    # Make API request
    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        results = data.get("results", [])
        if not results:
            return jsonify({"error": "No results found"}), 404
        closest_coords, closest_distance, locationid = find_closest_coordinates(user_lat, user_lon, results)

    if closest_coords:
        return jsonify({
            "closest_coordinates": closest_coords,
            "distance_km": closest_distance,
            "location_id": locationid
        })
    else:
        return jsonify({"error": "No valid coordinates found"}), 404


@app.route("/get-air-quality", methods=["GET"])
def get_air_quality():
    locationid = request.args.get("locationid")
    if not locationid:
        return jsonify({"error": "Location ID is required"}), 400

    url = f"https://api.openaq.org/v3/locations/{locationid}"
    headers = {"X-API-Key": API_KEY}

    # Make the request to Open AQ API
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return jsonify(response.json())  # Forward the API response to the front-end
    else:
        return jsonify({"error": "Failed to fetch data", "details": response.text}), response.status_code

if __name__ == "__main__":
    app.run(debug=True)


