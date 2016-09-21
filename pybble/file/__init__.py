import requests
import copy

from pybble.error import RubbleServerException, error_string_from_request
from urllib.parse import urljoin


class RubbleFile:

    def __init__(self, auth, config):
        self.auth = auth
        self.config = config
        self.PROTOCOL_PREFIX = "file:/"

    def get(self, path, **kwargs):
        """
        Path parameters

        PATH

            The file's path relative to the root folder of your domain.

        Returns the content of the file at PATH. The content-type is always text/plain.

        :param path:
        :return:
        """
        params = {}
        params.update(kwargs)

        url = urljoin(self.config['url']['api'], 'file/' + path)
        request = requests.get(url,
                               auth=self.auth,
                               params=params,
                               **self.config['default_request_kwargs'])

        if request.ok:
            return request.text
        else:
            raise RubbleServerException(error_string_from_request(request))

    def put(self, path, data, **kwargs):
        """
        Path parameters

            PATH

        The file's path relative to the root folder of your domain.

        Stores new content in the file at PATH. The content-type of the request
        body must be application/octet-stream. The MIME-type of the repository
        file stays the same as it was before. Note: this method is sometimes
        more useful than WebDAV PUT since it bypasses WebDAV locking, which can
        sometimes get stuck for certain clients.

        :param path:
        :return:
        """
        params = {}
        params.update(kwargs)

        request_kwargs = copy.deepcopy(self.config['default_request_kwargs'])
        request_kwargs['headers']['content-type'] = 'application/octet-stream'

        url = urljoin(self.config['url']['api'], 'file/' + path)
        request = requests.put(url,
                               auth=self.auth,
                               data=data,
                               params=params,
                               **request_kwargs)

        if request.ok:
            return True
        else:
            raise RubbleServerException(error_string_from_request(request))