from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from tickets.models import load_tickets, create_ticket, update_ticket_status

tickets_bp = Blueprint("tickets", __name__)


@tickets_bp.route("/", methods=["GET", "POST"])
@login_required
def list_tickets():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        desc = request.form.get("description", "").strip()
        severity = request.form.get("severity", "medium")
        ioc_value = request.form.get("ioc_value", "").strip()

        if not title or not desc:
            flash("Title and description are required", "danger")
        else:
            create_ticket(title, desc, severity, ioc_value, current_user.username)
            flash("Ticket created", "success")
            return redirect(url_for("tickets.list_tickets"))

    tickets = load_tickets()
    tickets_list = sorted(tickets.values(), key=lambda x: x["id"], reverse=True)
    return render_template("tickets.html", tickets=tickets_list)


@tickets_bp.route("/<ticket_id>", methods=["GET", "POST"])
@login_required
def ticket_detail(ticket_id):
    tickets = load_tickets()
    ticket = tickets.get(ticket_id)
    if not ticket:
        flash("Ticket not found", "danger")
        return redirect(url_for("tickets.list_tickets"))

    if request.method == "POST":
        new_status = request.form.get("status")
        if new_status in ("open", "in_progress", "closed"):
            update_ticket_status(ticket_id, new_status)
            flash("Status updated", "success")
            return redirect(url_for("tickets.ticket_detail", ticket_id=ticket_id))

    return render_template("ticket_detail.html", ticket=ticket)
