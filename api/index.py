import os
import sys

# Make the project root importable inside the serverless bundle
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app  # noqa: E402

app = create_app(os.getenv("FLASK_ENV", "production"))
