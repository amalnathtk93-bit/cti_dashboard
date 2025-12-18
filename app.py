from flask import Flask
from flask_login import LoginManager
import os
from dotenv import load_dotenv

# LOAD ENV FIRST
load_dotenv()

# CREATE APP FIRST
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "supersecretkey")

# IMPORT BLUEPRINTS (AFTER app exists)
from auth.routes import auth_bp
from dashboard.routes import dashboard_bp
from auth.models import User
from ioc.routes import ioc_bp
from tickets.routes import tickets_bp
from feeds.routes import feeds_bp
from routes.threat_map import threat_map

# LOGIN MANAGER
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)

# REGISTER BLUEPRINTS
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(dashboard_bp, url_prefix="/")
app.register_blueprint(ioc_bp, url_prefix="/ioc")
app.register_blueprint(tickets_bp, url_prefix="/tickets")
app.register_blueprint(feeds_bp, url_prefix="/feeds")

# 🔴 IMPORTANT FIX — API ROUTE FOR MAP
app.register_blueprint(threat_map, url_prefix="/api")

# RUN
if __name__ == "__main__":
    app.run(debug=True)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
