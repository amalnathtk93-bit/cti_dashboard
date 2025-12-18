from flask import Blueprint, render_template, request
from flask_login import login_required

from ioc.services import (
    lookup_ip,
    lookup_domain,
    lookup_url,
    lookup_hash,
    record_lookup,
)
from ioc.parsers import parse_vt_response

ioc_bp = Blueprint("ioc", __name__)


@ioc_bp.route("/lookup", methods=["GET", "POST"])
@login_required
def lookup():
    parsed = None
    error = None
    selected_type = "ip"
    value = ""

    if request.method == "POST":
        selected_type = request.form.get("ioc_type", "ip")
        value = request.form.get("value", "").strip()

        if not value:
            error = "Please enter a value."
        elif selected_type not in ("ip", "domain", "url", "hash"):
            error = "Unsupported IOC type."
        else:
            if selected_type == "ip":
                vt_json = lookup_ip(value)
            elif selected_type == "domain":
                vt_json = lookup_domain(value)
            elif selected_type == "url":
                vt_json = lookup_url(value)
            else:  # hash
                vt_json = lookup_hash(value)

            if vt_json is None:
                error = "Error contacting VirusTotal API. Check your VT_API_KEY and network."
            else:
                parsed = parse_vt_response(vt_json, selected_type)
                record_lookup(selected_type, value, parsed)

    return render_template(
        "lookup.html",
        error=error,
        parsed=parsed,
        selected_type=selected_type,
        value=value,
    )
