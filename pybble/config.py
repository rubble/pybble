import os
from urllib.parse import urljoin

from pybble import setup_params

#
# CONFIG
#

# URLs
ROOT_URL = os.environ.get("RUBBLE_SERVER_URL", "https://rubble2.labs.rubble.tech/")
API_URL = urljoin(ROOT_URL, "rubble/service/")

config = {
    "url": {
        "root": ROOT_URL,
        "api": API_URL,
    },
    "default_request_kwargs": {
        "verify": True,
        "headers": {
            "user-agent": "pybble {}".format(setup_params['version']),
            "content-type": "application/json",
        }
    }
}