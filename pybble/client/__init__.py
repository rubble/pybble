import os
import requests
from urllib.parse import urljoin

from pybble import setup_params
from pybble.config import config as default_config
from pybble.error import error_string_from_request, RubbleServerException

from pybble import (
    process,
    file,
    babylon,
    channel,
)


class Client:
    """The Rubble web services use HTTP Basic authentication for
        everything except for the URL paths /rubble/service/cluster-probe
        and /rubble/webdav/www/, which may be accessed without
        authentication. The cluster-probe service is intended for calls
        from the Azure load balancer to determine server
        responsiveness. The www WebDAV folder is intented for central
        management of various web resources that can be cached by the
        reverse proxy frontend. [This folder is not yet implemented, the
        files are currently duplicated on each frontend instance.]

        The authentication credentials consist of an API key and a
        secret. They function as the username and password in the HTTP
        Basic protocol. Application developers sign up in a separate web
        app where they can generate their own API keys and secrets. There
        are also master credentials used for bootstrapping and for
        intra-cluster communication.  A class to talk to the rubble
        service.

        Appendix A
        ----------

        Rubble facts can  either be set as a nested list otherwise known as
        JSON-encoded Rubble facts:

            [["completed","task23"],
             ["device_category","1","Mobile device"],
             ["leap_year"],
             "daylight_saving",
             ["f",["g","h"],["i","j","k"]]

        Or as plain Rubble rules:

            completed(task23);
            device_category(1,"Mobile device");
            leap_year;
            daylight_saving;
            f(g(h),i(j,k));

        See http://clip.dia.fi.upm.es/~vocal/public_info/seminar_notes/node32.html
    """

    def __init__(self, key="", password="", config=None):
        """
        :param key:
            Rubble server API key or username
        :param password:
            Rubble server API password or password
        :param config:
            Various config options that can be passed to modify the base config
        :type config:
            dict
        """

        # Specifying user and password in function call takes
        # precedence over environment variables, but if neither are specified
        # then raise an error.
        if not all([key, password]):
            key = os.environ.get("RUBBLE_API_KEY", key)
            password = os.environ.get("RUBBLE_API_PASSWORD", password)

        if not all([key, password]):
            raise ValueError(
                (
                 "You must either supply an API key and API password or "
                 "your key and password must be set as environment variables"
                )
            )
        # User must supply API key to talk to rubble
        self.auth = (key, password)

        # Set the default config and update it with any config the
        # users passes in
        if not config:
            self.config = default_config
        else:
            self.config.update(default_config)

        # Attach modules to the client
        self.process = process.RubbleProcess(auth=self.auth, config=self.config)
        self.file = file.RubbleFile(auth=self.auth, config=self.config)
        self.babylon = babylon.Babylon(auth=self.auth, config=self.config)

    def config(self, config=None):
        """
        Get the current configuration or set it if a new config object is
        given
        :return:
        """
        if config:
            self.config = self.config.update(config)
            return self.config
        else:
            return self.config

    def domain_info(self):
        """Returns a JSON object that contains some information about the
        client's credentials.

        This is easiest described via an example. Suppose an
        application authenticates with the API key Fv32O6HN9Abz and
        the secret password WvAQtZjIOAVnPluc, and this API key belongs
        to an account named acme. Then the response from this call
        will be {"domain":"acme","apikey":"Fv32O6HN9Abz"}.
        """
        url = urljoin(self.config['url']['api'], 'domaininfo')
        request = requests.get(url,
                               auth=self.auth,
                               **self.config['default_request_kwargs'])

        if request.ok:
            return request.json()
        else:
            raise RubbleServerException(error_string_from_request(request))