import json
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
TICKETS_FILE = os.path.join(BASE_DIR, "tickets.json")


def load_tickets():
    if not os.path.exists(TICKETS_FILE):
        return {}
    with open(TICKETS_FILE, "r") as f:
        return json.load(f)


def save_tickets(data):
    with open(TICKETS_FILE, "w") as f:
        json.dump(data, f, indent=4, default=str)


def create_ticket(title, description, severity, ioc_value, created_by):
    tickets = load_tickets()
    ticket_id = str(len(tickets) + 1)
    tickets[ticket_id] = {
        "id": ticket_id,
        "title": title,
        "description": description,
        "severity": severity,
        "ioc_value": ioc_value,
        "status": "open",
        "created_by": created_by,
        "created_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "updated_at": None
    }
    save_tickets(tickets)
    return tickets[ticket_id]


def update_ticket_status(ticket_id, status):
    tickets = load_tickets()
    if ticket_id in tickets:
        tickets[ticket_id]["status"] = status
        tickets[ticket_id]["updated_at"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        save_tickets(tickets)
        return tickets[ticket_id]
    return None
