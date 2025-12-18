from flask import Blueprint, render_template
from flask_login import login_required

from feeds.services import aggregate_feeds

feeds_bp = Blueprint("feeds", __name__)


@feeds_bp.route("/")
@login_required
def feeds_home():
    feeds = aggregate_feeds()
    return render_template("feeds.html", feeds=feeds)
