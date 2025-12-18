import json
import os
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
USERS_FILE = os.path.join(BASE_DIR, "users.json")

# =========================
# HARD CODED ADMIN
# =========================
STATIC_ADMIN_USERNAME = "admin"
STATIC_ADMIN_PASSWORD = "admin123"

MIN_PASSWORD_LENGTH = 6


class User(UserMixin):
    def __init__(self, id, username, password_hash="", role="analyst"):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.role = role

    # =========================
    # ROLE HELPERS
    # =========================
    @property
    def is_admin(self):
        return self.role == "admin"

    # =========================
    # FILE HELPERS (PUBLIC)
    # =========================
    @staticmethod
    def load_users():
        if not os.path.exists(USERS_FILE):
            return {}
        try:
            with open(USERS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}

    @staticmethod
    def save_users(data):
        with open(USERS_FILE, "w") as f:
            json.dump(data, f, indent=4)

    # =========================
    # PASSWORD HELPERS
    # =========================
    @staticmethod
    def _hash_password(password):
        return generate_password_hash(password)

    @staticmethod
    def set_password(user_id, new_password):
        users = User.load_users()
        if user_id in users:
            users[user_id]["password"] = User._hash_password(new_password)
            User.save_users(users)
            return True
        return False

    # =========================
    # VALIDATION
    # =========================
    @staticmethod
    def _valid_username(username):
        return bool(username and len(username) >= 3)

    @staticmethod
    def _valid_password(password):
        return bool(password and len(password) >= MIN_PASSWORD_LENGTH)

    # =========================
    # USER LIST
    # =========================
    @staticmethod
    def list_users(include_admin=True):
        users = []

        if include_admin:
            users.append(User("0", STATIC_ADMIN_USERNAME, "", "admin"))

        data = User.load_users()
        for uid, u in data.items():
            users.append(
                User(
                    uid,
                    u.get("username"),
                    u.get("password"),
                    u.get("role", "analyst"),
                )
            )
        return users

    # =========================
    # CREATE USER
    # =========================
    @staticmethod
    def create(username, password, role="analyst"):
        users = User.load_users()

        if not User._valid_username(username):
            return None

        if not User._valid_password(password):
            return None

        if username == STATIC_ADMIN_USERNAME:
            return None

        if role not in ("admin", "analyst"):
            role = "analyst"

        for u in users.values():
            if u.get("username") == username:
                return None

        existing_ids = [int(uid) for uid in users.keys()] if users else [0]
        user_id = str(max(existing_ids) + 1)

        users[user_id] = {
            "username": username,
            "password": User._hash_password(password),
            "role": role,
        }

        User.save_users(users)
        return User(user_id, username, users[user_id]["password"], role)

    # =========================
    # AUTHENTICATION
    # =========================
    @staticmethod
    def authenticate(username, password):
        # SYSTEM ADMIN
        if username == STATIC_ADMIN_USERNAME and password == STATIC_ADMIN_PASSWORD:
            return User("0", STATIC_ADMIN_USERNAME, "", "admin")

        users = User.load_users()
        for uid, u in users.items():
            if u.get("username") == username and check_password_hash(
                u.get("password", ""), password
            ):
                return User(uid, username, u["password"], u.get("role", "analyst"))

        return None

    # =========================
    # USER LOADER (Flask-Login)
    # =========================
    @staticmethod
    def get_by_id(user_id):
        if str(user_id) == "0":
            return User("0", STATIC_ADMIN_USERNAME, "", "admin")

        users = User.load_users()
        if user_id in users:
            u = users[user_id]
            return User(
                user_id,
                u.get("username"),
                u.get("password"),
                u.get("role", "analyst"),
            )
        return None
import datetime

AUDIT_FILE = os.path.join(BASE_DIR, "audit_log.json")


class AuditLog:
    @staticmethod
    def _load():
        if not os.path.exists(AUDIT_FILE):
            return []
        try:
            with open(AUDIT_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return []

    @staticmethod
    def _save(data):
        with open(AUDIT_FILE, "w") as f:
            json.dump(data, f, indent=4)

    @staticmethod
    def log(actor, action, target=None):
        logs = AuditLog._load()
        logs.insert(0, {
            "time": datetime.datetime.utcnow().isoformat() + "Z",
            "actor": actor,
            "action": action,
            "target": target
        })
        AuditLog._save(logs)

    @staticmethod
    def list_logs(limit=200):
        return AuditLog._load()[:limit]
