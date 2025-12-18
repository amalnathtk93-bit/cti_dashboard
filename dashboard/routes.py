from flask import Blueprint, render_template
from flask_login import login_required, current_user

from ioc.services import get_stats, get_recent_lookups, get_globe_points

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@login_required
def home():
    stats = get_stats()
    recent = get_recent_lookups(limit=5)
    globe_points = get_globe_points()
    return render_template(
        "dashboard.html",
        stats=stats,
        user=current_user,
        recent=recent,
        globe_points=globe_points
    )
