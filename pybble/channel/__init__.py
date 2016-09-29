import requests
from urllib.parse import urljoin

from pybble.error import RubbleServerException, error_string_from_request


class RubbleChannel:

    def __init__(self, config):
        self.config = config

    # todo: format to numpy conventions
    def update(self, channel, pid):
        """
        Updates the channel alias registry. This method handles both creation,
        updating, and deletion of channel aliases. The request body must have
        content-type application/json and consist of a JSON object.

        Args:

            channel (str): The channel alias
            pid (int):  The process id to set the channel alias to

        Response body properties

        error (optional)

            An error message (a JSON string). This property is omitted if the
            operation was successful.

        Example: If the name foo is registered as an alias for the process ID
        17, then sending a message to the channel foo will be equivalent to
        sending a message to the channel pid(17).

        To create a new alias, use a new name. To delete an existing alias
        entry, specify the process ID "0".
        """

        payload = {
            'channel': channel,
            'pid': str(pid),
        }

        url = urljoin(self.config['url']['api'], 'chanupdate')

        request = requests.post(url,
                                params=payload,
                                **self.config['default_request_kwargs'])

        if request.ok:
            return request.json()
        else:
            raise RubbleServerException(error_string_from_request(request))

    # todo: format according to numpy docstring conventions
    def list(self, **kwargs):
        """Retrieves the list of registered channel aliases.

        Keyword

        includeGlobal=INCLUDEGLOBAL (optional)

            Set this to 1 to include globally scoped channel aliases, common
            for all domains. The default value is 0.

        domain=DOMAIN (optional)

            Set this to * to list only globally scoped channel aliases. Any
            other value of DOMAIN will be ignored.

        skipItems=SKIPITEMS (optional)

            Skip the first SKIPITEMS number of items when creating the list.
            The default value is 0. For pagination.

        maxItems=MAXITEMS (optional)

            The maximum number of items to return in the list. The default
            value is 2147483647 (231-1). For pagination.

        The response is a JSON object: {"result":[…]}. Each element of the JSON
        array result is a JSON object: {…}

        :return:
        """
        params = {}
        params.update(kwargs)
        url = urljoin(self.config['url']['api'], 'chanlist')
        request = requests.get(url, params=params,
                               **self.config['default_request_kwargs'])

        if request.ok:
            return request.json()
        else:
            raise RubbleServerException(error_string_from_request(request))