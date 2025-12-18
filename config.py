# config.py
import os
from dotenv import load_dotenv
from pymongo import MongoClient

BASE_DIR = os.path.dirname(__file__)
env_path = os.path.join(BASE_DIR, ".env")
load_dotenv(dotenv_path=env_path)

MONGO_URI = os.getenv("MONGO_URI")  # Atlas only
VT_API_KEY = os.getenv("VT_API_KEY")

if not MONGO_URI:
    raise ValueError("MONGO_URI is not set in .env")
if not VT_API_KEY:
    raise ValueError("VT_API_KEY is not set in .env")

db = None
DB_OK = False

print("Using Mongo URI:", MONGO_URI)

try:
    client = MongoClient(
        MONGO_URI,
        tls=True,
        tlsAllowInvalidCertificates=True,  # dev only
        serverSelectionTimeoutMS=10000
    )
    client.admin.command("ping")   # test
    print("✅ Connected to MongoDB Atlas successfully.")
    db = client["cti_dashboard"]
    DB_OK = True
except Exception as e:
    print("❌ MongoDB connection failed (Atlas):")
    print(e)
    raise   # stop app if Atlas doesn’t work (cloud-only mode)
