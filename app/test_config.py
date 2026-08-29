# test_config.py
import os
from dotenv import load_dotenv
from app.config import config

# Load .env file
load_dotenv()

print("=== Environment Variables ===")
print(f"DATABASE_URL: {os.getenv('DATABASE_URL')}")
print(f"FLASK_ENV: {os.getenv('FLASK_ENV')}")
print(f"SECRET_KEY: {os.getenv('SECRET_KEY')}")

print("\n=== Config Values ===")
cfg = config['development']
print(f"SQLALCHEMY_DATABASE_URI: {cfg.SQLALCHEMY_DATABASE_URI}")
print(f"DEBUG: {cfg.DEBUG}")
print(f"CORS_ORIGINS: {cfg.CORS_ORIGINS}")