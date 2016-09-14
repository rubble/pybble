import os
import pybble
import requests

# Create a connection to Rubble using Pybble
RUBBLE_API_KEY = os.environ.get('RUBBLE_API_KEY')
RUBBLE_API_PASSWORD = os.environ.get('RUBBLE_API_PASSWORD')
auth = (RUBBLE_API_KEY, RUBBLE_API_PASSWORD)

config = {
    "base_url": "http://localhost:8082/",
    "verify_SSL": False,
}

rubble = pybble.RubbleREST(auth=auth,
                           config=config)