import os
import base64
from datetime import datetime

import requests
from dotenv import load_dotenv

from ioc.parsers import parse_vt_response

load_dotenv()
VT_API_KEY = os.getenv("VT_API_KEY")
BASE_URL = "https://www.virustotal.com/api/v3"

if not VT_API_KEY:
    raise ValueError("VT_API_KEY is not set in .env")

HEADERS = {
    "x-apikey": VT_API_KEY
}

# In-memory IOC history
LOOKUPS = []  # each: {ioc_type, value, parsed, created_at}

# Simple country → approximate lat/lon mapping so globe always works
COUNTRY_COORDS = {
    "IN": (20.5937, 78.9629),
    "US": (37.0902, -95.7129),
    "GB": (55.3781, -3.4360),
    "DE": (51.1657, 10.4515),
    "FR": (46.2276, 2.2137),
    "JP": (36.2048, 138.2529),
    "CN": (35.8617, 104.1954),
    "BR": (-14.2350, -51.9253),
    "RU": (61.5240, 105.3188),
    "AU": (-25.2744, 133.7751),
    "CA": (56.1304, -106.3468),
    "SG": (1.3521, 103.8198),
    "NL": (52.1326, 5.2913),
    "ES": (40.4637, -3.7492),
    "IT": (41.8719, 12.5674),
    "ZA": (-30.5595, 22.9375),
}


def _country_to_coords(code: str):
    if not code:
        return None, None
    code = code.upper()
    return COUNTRY_COORDS.get(code, (None, None))


def vt_get(url: str):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=20)
        if resp.status_code == 200:
            return resp.json()
        else:
            print("VirusTotal error:", resp.status_code, resp.text)
            return None
    except Exception as e:
        print("Error calling VirusTotal:", e)
        return None


def lookup_ip(ip: str):
    url = f"{BASE_URL}/ip_addresses/{ip}"
    return vt_get(url)


def lookup_domain(domain: str):
    url = f"{BASE_URL}/domains/{domain}"
    return vt_get(url)


def lookup_hash(file_hash: str):
    url = f"{BASE_URL}/files/{file_hash}"
    return vt_get(url)


def lookup_url(raw_url: str):
    """
    VT v3 URL lookup uses URL-safe base64 of the URL as the ID.
    """
    url_id = base64.urlsafe_b64encode(raw_url.encode("utf-8")).decode("utf-8").strip("=")
    url = f"{BASE_URL}/urls/{url_id}"
    return vt_get(url)


def record_lookup(ioc_type: str, value: str, parsed: dict):
    """
    Store lookup result in memory. We keep it simple: parsed already
    contains country for IPs, which we later convert to geo coords.
    """
    LOOKUPS.append(
        {
            "ioc_type": ioc_type,
            "value": value,
            "parsed": parsed,
            "created_at": datetime.utcnow(),
        }
    )


def get_recent_lookups(limit: int = 5):
    return sorted(LOOKUPS, key=lambda x: x["created_at"], reverse=True)[:limit]


def get_stats():
    total = len(LOOKUPS)
    malicious = sum(1 for x in LOOKUPS if x["parsed"] and x["parsed"]["malicious"] > 0)
    harmless = sum(1 for x in LOOKUPS if x["parsed"] and x["parsed"]["malicious"] == 0)
    suspicious = sum(1 for x in LOOKUPS if x["parsed"] and x["parsed"]["suspicious"] > 0)
    return {
        "total_iocs": total,
        "malicious": malicious,
        "harmless": harmless,
        "suspicious": suspicious,
    }


def get_globe_points():
    """
    Build data for the 3D globe from IOC lookups.
    For IPs we use VT's country code to place a point on the map.
    Each point: {lat, lng, severity, value, country, city}
    """
    points = []
    for x in LOOKUPS:
        p = x.get("parsed") or {}
        ioc_type = x.get("ioc_type")

        # Only IPs go on the globe for now
        if ioc_type != "ip":
            continue

        country_code = (p.get("geo_country") or p.get("country") or "").upper()
        lat, lon = _country_to_coords(country_code)
        if lat is None or lon is None:
            continue

        severity = "harmless"
        if p.get("malicious", 0) > 0:
            severity = "malicious"
        elif p.get("suspicious", 0) > 0:
            severity = "suspicious"

        points.append(
            {
                "lat": lat,
                "lng": lon,
                "severity": severity,
                "value": p.get("value"),
                "country": country_code,
                "city": p.get("geo_city"),
            }
        )

    return points
