import requests
import datetime
from urllib.parse import urljoin

from pybble import time
from pybble.error import RubbleServerException, error_string_from_request


class RubbleProcess:

    def __init__(self, auth, config):
        self.auth = auth
        self.config = config

    def call(self, terms, pid, **kwargs):
        """Synchronously sends a message consisting of Herbrand terms to
        a designated channel.

        Parameters
        ----------

        terms: list or dict
            Rubble facts or more generally Herbrand terms. See appendix A in
            class docstring.

        channel: str, optional
            Identifies the recipient process by it's registered
            channel name

        pid: int, optional
            Identifies the recipient process by it's process ID.

        wrap_input_from: str, optional
            Identifies the sender to the receiving process. If supplied, every
            term X in the message payload is wrapped as input(FROM,X). This is
            useful if the receiving process has rules with conditions on
            input/2 terms. It is mandatory to use this when doing cross-domain
            messaging, for security reasons. The pseudo-channel default is
            always an acceptable value for FROM.

        Returns
        -------
        response: dict or request
            A dict converted from the JSON object. {"output":[…]} on success, or
            {"error":"MESSAGE"} if an error occurred. The request will be returned
            if there is an error actually making the request

        If the rules triggered by this message results in new outgoing
        messages to the pseudo-channel default, the terms in these
        messages are delivered to the client in the response property
        output, encoded as a JSON array.

        The message is not enqueued, but rather bypasses any pending
        enqueued messages and is delivered in the same transaction as
        the request.
        """

        # create the payload and update with kwargs, channel is represented
        # by the string pid(N) where N is the numeric process ID
        params = {
            'channel': 'pid(%s)' % pid
        }

        # URL arguement uses hyphens, but hyphens cannot be used in
        # dict keys.
        if 'wrap_input_from' in kwargs:
            params['wrap-input-from'] = kwargs['wrap_input_from']
            del kwargs['wrap_input_from']

        if 'pid' in kwargs:
            params['channel'] = 'pid(%d)' % kwargs['pid']
            del kwargs['pid']

        if 'pid' and 'channel' in kwargs:
            raise ValueError("""Ambiguous. Either use either a PID or a channel
            alias to select the channel to call to. Not both.
            """)

        params.update(kwargs)

        # join the api url to the method call
        url = urljoin(self.config['url']['api'],
                      'call?channel={channel}'.format(**params), True)

        request = requests.post(url,
                                auth=self.auth,
                                json=terms,
                                **self.config['default_request_kwargs'])

        if request.ok:
            return request.json()
        else:
            raise RubbleServerException(error_string_from_request(request))

    def send(self, terms, pid, **kwargs):
        """Sends a message consisting of JSON-encoded Herbrand terms to the
        designated channel.

        Parameters
        ----------

        terms: str or list
            Rubble facts or more generally Herbrand terms.  See appendix A in
            module docstring.

        channel: str, optional
            Identifies the recipient process by it's registered
            channel name

        pid: int, optional
            Identifies the recipient process by it's process ID.

        when: datetime, optional
            When to deliver the message.

        For a description of the JSON Rubble format, see Appendix A,
        JSON-encoded Rubble facts.

        The response is an empty JSON object {} on success, or
        {"error":"MESSAGE"} if an error occurred. Note: success only
        means that the message was successfully enqueued. Due to the
        asynchronous nature of message sending, some errors may occur
        after the API response has been committed.
        """

        # create the payload and update with kwargs, channel is represented
        # by the string pid(N) where N is the numeric process ID
        params = {
            'channel': 'pid(%s)' % pid
        }

        # URL arguement uses hyphens, but hyphens cannot be used in
        # dict keys.
        if 'wrap_input_from' in kwargs:
            params['wrap-input-from'] = kwargs['wrap_input_from']
            del kwargs['wrap_input_from']

        # Expect a datetime object, convert it to milliseconds
        # since epoch
        if 'when' in kwargs:
            if type(kwargs['when']) is not datetime.datetime:
                raise ValueError("""The keyword 'when' must be a datetime
                object.
                """)

            kwargs['when'] = self.datetime_to_epoch(kwargs['when'])
            params['when'] = kwargs['when']

        if 'pid' in kwargs:
            params['channel'] = 'pid(%d)' % kwargs['channel']

        params.update(kwargs)

        # join the api url to the method call
        url = urljoin(self.config['url']['api'], 'send')

        request = requests.post(url,
                                auth=self.auth,
                                json=terms,
                                params=params,
                                **self.config['default_request_kwargs'])

        if request.ok:
            return request.json()
        else:
            raise RubbleServerException(error_string_from_request(request))

    def get(self, pid, prettyprint=True, **kwargs):
        """
        Retrieves a process. The response is a JSON object: {"content":{…}} on
        success, or {"error":"MESSAGE"} if no process with the specified pid
        exists or if the caller isn't allowed to access it.

        Arguments
        ---------

        pid: int

            A numeric process ID that identifies the process.

        prettyprint: boolean, optional

            False retrieves the process state exactly as stored in the
            database, and true prettyprints the process state data after
            retrieval, for prettier display in the browser
            interface. This feature is still a bit rudimentary.

        Returns
        -------

        pid: int

            For convenience. Same as the query parameter PID. The
            process ID of the newly created process. Note: this is a
            JSON string (of digits), not a JSON number.

        modtime: int

            Time of last modification. This is a time coordinate,
            approximately the number of milliseconds since 00:00:00
            UTC on January 1, 1970. Note: this is a JSON number, not a
            string.

        domain: str

            The domain of this process. For a non-privileged
            application this is always the same as the caller's
            authenticated domain.

        rulesref: str

            See documentation for processcreate.

        factsformat: list

            See documentation for processcreate.

        facts: list

            See documentation for processcreate.

        trapstate (optional)

            An optional string containing an XML document that
            represents any exceptional processing state. See below for
            an explanation of this XML document.

        Example of a response body:

            {
              "content":
              {
                "pid":"4711",
                "modtime":1367237523740,
                "domain":"acme",
                "rulesref":"file:/foo.rubble",
                "factsformat":1,
                "facts":"empty(glass); empty(wallet); full(moon);"
              }
            }

        If no process exists with the specified PID, or if the application
        isn't allowed to access it, an error message is returned:

            {
                "error": "No such process or unauthorized access"
            }

        Example of a trapstate property value:

            <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
            <trapstate>
                <timestamp>1368101400107</timestamp>
                <cause>ERROR</cause>
                <description>Inference failure: CONTRADICTION crazy_fact</description>
                <triggering-message>input(pid(42),crazy_fact);</triggering-message>
                <reschedule-delay>60000</reschedule-delay>
                <discard-after>172800000</discard-after>
            </trapstate>

        The above example describes a process rule execution that was aborted
        due to detection of a logical contradiction. No more messages will be
        received by this process instance until the trapstate has been cleared,
        or unless a specified condition holds. Any messages not received by
        this process while the trapstate is non-null will be delayed by the
        number of milliseconds specified by <reschedule-delay>. If
        <discard-after> milliseconds have passed since the time specified by
        <timestamp>, the message will be silently discarded instead.

        The value of the <cause> element determines how execution proceeds.

        Possible values of <cause>

        ERROR

            Set by syntax errors and exceptions during rule execution.

        PAUSED

            Set intentionally when there is a need to pause further processing
            for this process instance, for administrative or debugging reasons.

        PAUSE-ON-CONDITION

            Used for debugging. Execution proceeds normally despite trapstate
            being non-null, but at the end of each process-state transition a
            logical condition is evaluated. If this condition is true, the
            trapstate <cause> is changed to PAUSED, stopping further execution.
            The logical condition is specified by a fragment of Rubble code in
            the element <pause-condition> in the trapstate.

        The element <triggering-message> contains the fact terms of the input
        message that caused the trap. Native Rubble syntax is used for these
        terms. This is for display & debugging only. Any changes made to this
        data are ignored, it's only a copy of the pending message stored in the
        message queue.

        """
        params = {
            "pid": str(pid),
            "prettyprint": 1 if prettyprint else 0,
        }

        # add kwargs as params to the payload
        params.update(kwargs)

        # join the api url to the method call
        url = urljoin(self.config['url']['api'], 'process')

        request = requests.get(url,
                               auth=self.auth,
                               params=params,
                               **self.config['default_request_kwargs'])

        if request.ok:
            return request.json()
        else:
            raise RubbleServerException(error_string_from_request(request))

    def create(self, rulesref, **kwargs):
        """
        Creates a new Rubble process. The request body must have
        content-type application/json and consist of a JSON object.

        Keyword arguements
        -----------------------

        rulesref

            A string that specifies the rule file that contains
            the Rubble code which controls this process. This string should
            have either the format file:/PATH or the format
            file://DOMAIN/PATH. For compatibility with RFC 3986 the variant
            for var in collection:
            mat file:///PATH is accepted as equivalent to the single-slash
            format.

        factsformat (optional)

            Specifies the storage format of the Rubble process state for
            this process. If provided, this property is either one of the
            strings native, xml, json, or the number 1 or 2. The
            alternatives xml or 2 cause the facts to be stored internally
            in XML format and require the facts property to be supplied as
            a string containing the initial XML code. The alternatives
            native or 1 cause the facts to be stored internally in Rubble
            native format and require the facts property to be supplied as
            a string containing the initial Rubble code. The alternative
            json causes the facts to be stored internally in Rubble native
            format and requires the facts property to be supplied as a
            JSON array (see Appendix A, JSON-encoded Rubble facts). The
            default value for factsformat is json.

        facts (optional)

            The initial process state, in the syntax specified by
            factsformat. The default syntax is a JSON array (see Appendix
            A, JSON-encoded Rubble facts). The default value is an empty
            set of facts. An empty string is always legal here, in the XML
            case it will be automatically converted into the empty root
            element <rubble/>.

        trapstate (optional)

            An optional string containing an XML document that represents
            any exceptional processing state. If this string is omitted or
            left blank, normal processing will be assumed. See
            documentation of process for details. This property is
            typically omitted at process creation.

        The response is a JSON object.

        Response body properties
        ------------------------

        pid

            The process ID of the newly created process. Note: this is a
            JSON string (of digits), not a JSON number.

        """

        payload = {
            'rulesref': rulesref,
        }

        # add kwargs as params to the payload
        payload.update(kwargs)

        # join the api url to the method call
        url = urljoin(self.config['url']['api'], 'processcreate')

        request = requests.post(url,
                                auth=self.auth,
                                json=payload,
                                **self.config['default_request_kwargs'])

        if request.ok:
            return request.json()
        else:
            raise RubbleServerException(error_string_from_request(request))

    def update(self, rulesref, pid, **kwargs):
        """
        Updates a Rubble process. The request body must have content-type
        application/json and consist of a JSON object.

        Arguments
        ---------

        pid

            The process ID of the process to update. Note: this must
            be a JSON string (of digits), not a JSON number.

        rulesref

            See docstring for processcreate.

        Keyword arguements
        ------------------

        factsformat (optional)

            See documentation for processcreate.

        facts (optional)

            See documentation for processcreate.

        trapstate (optional)

            See documentation for processcreate.

        Note: the optional properties are defaulted in the same
        way as for processcreate, i.e. they are not defaulted to
        their stored values.

        The response is an empty JSON object {} on success, or
        {"error":"Unauthorized access"} if the caller didn't have
        permission.

        """

        payload = {
            "pid": str(pid),
            "rulesref": rulesref,
        }

        # add kwargs as params to the payload
        payload.update(**kwargs)

        # join the api url to the method call
        url = urljoin(self.config['url']['api'], 'processupdate')

        request = requests.post(url,
                                auth=self.auth,
                                json=payload,
                                **self.config['default_request_kwargs'])

        if request.ok:
            return request.json()
        else:
            raise RubbleServerException(error_string_from_request(request))

    def delete(self, pid):
        """
        Deletes the process specified by the PID.

        pid=PID

            A numeric process ID that identifies the process. On success, the
            response is an empty JSON object: {}. If no process exists with the
            specified PID, or if the application isn't allowed to access it, an
            error message is returned:

                {
                    "error": "No such process or unauthorized access"
                }

            Note: the repository file that controls the process will not be
            deleted since it may be of use for other process instances.
        """
        url = urljoin(self.config['url']['api'], 'process')
        request = requests.delete(url,
                                  auth=self.auth,
                                  params={'pid': pid},
                                  **self.config['default_request_kwargs'])

        if request.ok:
            return request.json()
        else:
            raise RubbleServerException(error_string_from_request(request))

    # todo: format to numpy conventions
    def list(self):
        """
        Retrieves a list of process IDs and some associated metadata.

        Keyword arguments:

        pidBegin -- A lower limit for the process IDs listed. The default value is 0. For pagination.
        maxItems -- The maximum number of items to return in the list. The default value is 2147483647 (231-1). For pagination.

        The response is a JSON object: {"result":[…]}. Each element of the JSON
        array result is a JSON object: {…}.

        Response:

        pid

            The process ID, as a JSON string.

        domain

            See documentation for process.

        modtime

            See documentation for process.

        type

            This is either rules or script, depending on the process type.

        This web service call is mainly intended for the Rubble administration
        console.
        """
        url = urljoin(self.config['url']['api'], 'processlist')
        request = requests.get(url,
                               auth=self.auth,
                               **self.config['default_request_kwargs'])

        if request.ok:
            return request.json()
        else:
            raise RubbleServerException(error_string_from_request(request))