from flask import Blueprint, jsonify
import requests
import os
from dotenv import load_dotenv

# LOAD ENV
load_dotenv()

threat_map = Blueprint("threat_map", __name__)

ABUSEIPDB_API_KEY = os.getenv("ABUSEIPDB_API_KEY")


@threat_map.route("/threat-map", methods=["GET"])
def threat_map_data():
    if not ABUSEIPDB_API_KEY:
        return jsonify([])

    headers = {
        "Key": ABUSEIPDB_API_KEY,
        "Accept": "application/json"
    }

    response = requests.get(
        "https://api.abuseipdb.com/api/v2/blacklist",
        headers=headers,
        params={
            "confidenceMinimum": 85,
            "limit": 20
        },
        timeout=20
    )

    if response.status_code != 200:
        return jsonify([])

    data = response.json().get("data", [])

    threats = []
    for ip in data:
        threats.append({
            "ip": ip.get("ipAddress"),
            "country": ip.get("countryCode"),
            "risk": "malicious",
            "lat": ip.get("latitude"),
            "lon": ip.get("longitude")
        })

    return jsonify(threats)
