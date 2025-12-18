from datetime import datetime


def parse_vt_response(vt_json: dict, ioc_type: str):
    """
    Extract important fields from VirusTotal response.
    Supports ip, domain, url, file (hash).
    Returns a dict with friendly fields or None.
    """
    if not vt_json or "data" not in vt_json:
        return None

    data = vt_json.get("data", {})
    attributes = data.get("attributes", {})
    last_analysis_stats = attributes.get("last_analysis_stats", {})

    harmless = last_analysis_stats.get("harmless", 0)
    malicious = last_analysis_stats.get("malicious", 0)
    suspicious = last_analysis_stats.get("suspicious", 0)
    undetected = last_analysis_stats.get("undetected", 0)

    last_ts = attributes.get("last_analysis_date")
    last_analysis_date = None
    if isinstance(last_ts, (int, float)):
        try:
            last_analysis_date = datetime.utcfromtimestamp(last_ts).strftime(
                "%Y-%m-%d %H:%M:%S UTC"
            )
        except Exception:
            last_analysis_date = str(last_ts)

    parsed = {
        "ioc_type": ioc_type,
        "value": data.get("id"),
        "harmless": harmless,
        "malicious": malicious,
        "suspicious": suspicious,
        "undetected": undetected,
        "last_analysis_date": last_analysis_date,
        "reputation": attributes.get("reputation"),
        # IP-specific
        "country": attributes.get("country"),
        "as_owner": attributes.get("as_owner"),
        # Domain/URL-specific
        "categories": attributes.get("categories"),
        "tags": attributes.get("tags"),
        "type_description": attributes.get("type_description"),
        "meaningful_name": attributes.get("meaningful_name"),
    }

    return parsed
