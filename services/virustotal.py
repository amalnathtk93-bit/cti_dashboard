# services/virustotal.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()
VT_API_KEY = os.getenv("VT_API_KEY")
BASE_URL = "https://www.virustotal.com/api/v3"

if not VT_API_KEY:
    raise ValueError("VT_API_KEY is not set in .env")

headers = {
    "x-apikey": VT_API_KEY
}


def lookup_ip(ip: str):
    """
    Look up an IP address in VirusTotal.
    Returns parsed JSON data or None if error.
    """
    url = f"{BASE_URL}/ip_addresses/{ip}"
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code == 200:
            return resp.json()
        else:
            print("VirusTotal IP error:", resp.status_code, resp.text)
            return None
    except Exception as e:
        print("Error calling VirusTotal for IP:", e)
        return None


def lookup_domain(domain: str):
    """
    Look up a domain in VirusTotal.
    Returns parsed JSON data or None if error.
    """
    url = f"{BASE_URL}/domains/{domain}"
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code == 200:
            return resp.json()
        else:
            print("VirusTotal Domain error:", resp.status_code, resp.text)
            return None
    except Exception as e:
        print("Error calling VirusTotal for domain:", e)
        return None
