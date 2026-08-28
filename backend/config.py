import os

from dotenv import load_dotenv

load_dotenv()

# Set this in your environment or in a local .env file. It defaults to a local
# database named "podclub" so no JSON file is used for application data.
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://localhost/podclub')
FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost:5174').rstrip('/')
HOST = '0.0.0.0'
PORT = 5000
