import os
from pybble.client import Client

# Create a connection to Rubble using Pybble
RUBBLE_API_KEY = os.environ.get('RUBBLE_API_KEY')
RUBBLE_API_PASSWORD = os.environ.get('RUBBLE_API_PASSWORD')
RUBBLE_SERVER_URL = os.environ.get('RUBBLE_SERVER_URL', "http://localhost:8082/")

auth = (RUBBLE_API_KEY, RUBBLE_API_PASSWORD)

config = {
    "url": {
        "base": RUBBLE_SERVER_URL,
    },
    "default_request_kwargs": {
        "verify": False,
    }
}

rubble = Client(key=RUBBLE_API_KEY, password=RUBBLE_API_PASSWORD, config=config)

