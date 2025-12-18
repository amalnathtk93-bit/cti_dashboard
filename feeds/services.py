import os
import requests
from dotenv import load_dotenv

load_dotenv()

OTX_API_KEY = os.getenv("OTX_API_KEY")
ABUSEIPDB_API_KEY = os.getenv("ABUSEIPDB_API_KEY")
SHODAN_API_KEY = os.getenv("SHODAN_API_KEY")


def fetch_otx_pulses(limit=5):
    """
    AlienVault OTX - basic example pulling subscribed pulses.
    Needs OTX_API_KEY.
    """
    if not OTX_API_KEY:
        return []

    url = "https://otx.alienvault.com/api/v1/pulses/subscribed"
    headers = {"X-OTX-API-KEY": OTX_API_KEY}
    try:
        resp = requests.get(url, headers=headers, timeout=20)
        if resp.status_code != 200:
            print("OTX error:", resp.status_code, resp.text)
            return []
        data = resp.json()
        items = []
        pulses = data.get("results", [])[:limit]
        for p in pulses:
            indicators = p.get("indicators", [])
            if not indicators:
                continue
            ind = indicators[0]
            items.append(
                {
                    "source": "OTX",
                    "type": ind.get("type"),
                    "indicator": ind.get("indicator"),
                    "severity": "high",
                    "description": p.get("name"),
                }
            )
        return items
    except Exception as e:
        print("OTX exception:", e)
        return []


def fetch_abuseipdb_blacklist(limit=10):
    """
    AbuseIPDB blacklist.
    Needs ABUSEIPDB_API_KEY.
    """
    if not ABUSEIPDB_API_KEY:
        return []

    url = "https://api.abuseipdb.com/api/v2/blacklist"
    headers = {"Key": ABUSEIPDB_API_KEY, "Accept": "application/json"}
    try:
        resp = requests.get(url, headers=headers, timeout=20)
        if resp.status_code != 200:
            print("AbuseIPDB error:", resp.status_code, resp.text)
            return []
        data = resp.json()
        ips = data.get("data", [])[:limit]
        items = []
        for ip in ips:
            items.append(
                {
                    "source": "AbuseIPDB",
                    "type": "IP",
                    "indicator": ip.get("ipAddress"),
                    "severity": "high",
                    "description": f"Abuse score: {ip.get('abuseConfidenceScore')} / ISP: {ip.get('isp')}",
                }
            )
        return items
    except Exception as e:
        print("AbuseIPDB exception:", e)
        return []


def fetch_shodan_sample(limit=5):
    """
    Shodan search example (exposed RDP).
    Needs SHODAN_API_KEY.
    """
    if not SHODAN_API_KEY:
        return []

    query = "port:3389"
    url = f"https://api.shodan.io/shodan/host/search?key={SHODAN_API_KEY}&query={query}"
    try:
        resp = requests.get(url, timeout=20)
        if resp.status_code != 200:
            print("Shodan error:", resp.status_code, resp.text)
            return []
        data = resp.json()
        matches = data.get("matches", [])[:limit]
        items = []
        for m in matches:
            ip = m.get("ip_str")
            port = m.get("port")
            org = m.get("org")
            items.append(
                {
                    "source": "Shodan",
                    "type": "IP",
                    "indicator": f"{ip}:{port}",
                    "severity": "medium",
                    "description": f"Exposed service detected. Org: {org}",
                }
            )
        return items
    except Exception as e:
        print("Shodan exception:", e)
        return []


def aggregate_feeds():
    """
    Combine all enabled feeds into a single list.
    If an API key is missing, that feed is simply skipped.
    """
    all_items = []
    all_items.extend(fetch_otx_pulses(limit=5))
    all_items.extend(fetch_abuseipdb_blacklist(limit=10))
    all_items.extend(fetch_shodan_sample(limit=5))
    return all_items
