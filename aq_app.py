from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

# Enable CORS for all domains
CORS(app)

# Open AQ API Key
API_KEY = os.environ['OPENAQ_API_KEY']

# Endpoint for fetching air quality data
@app.route("/get-air-quality", methods=["GET"])
def get_air_quality():
    locationid = request.args.get("locationid")
    if not locationid:
        return jsonify({"error": "Location ID is required"}), 400

    url = f"https://api.openaq.org/v3/locations?city={locationid}"
    headers = {"X-API-Key": API_KEY}

    # Make the request to Open AQ API
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return jsonify(response.json())  # Forward the API response to the front-end
    else:
        return jsonify({"error": "Failed to fetch data", "details": response.text}), response.status_code

if __name__ == "__main__":
    app.run(debug=True)
