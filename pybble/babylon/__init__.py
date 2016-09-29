import sys
import requests
import copy

from urllib.parse import urljoin
from xml.etree import ElementTree

from pybble.error import RubbleServerException, error_string_from_request


def parse(xml):
    """
    Given the babylon XML return a list of dictionaries that represent the babylon
    XML
    :param xml:
    :return:
    """
    et = ElementTree.fromstring(xml)

    babylon_dict = {}

    symbols = et.findall("symbols")

    # Boilerplate rules. Split into lines and clear any lines that are empty.
    boilerplate_rules = [line.strip() for line
                         in et.find('boilerplate-rules').text.split('\n')
                         if not line.strip() is ""
                         ]

    babylon_dict['boilerplate-rules'] = boilerplate_rules

    # Symbols
    babylon_dict['symbols'] = {}

    for symbol in symbols:
        class_ = symbol.get('class')

        if class_ not in babylon_dict['symbols']:
            babylon_dict['symbols'][class_] = []

        babylon_dict['symbols'][class_].append(symbol.text.strip())


    # Macros
    macros = et.findall("macro")

    for macro in macros:

        rule = [line.strip() for line
                in macro.find('rules').text.split('\n')
                if not line.strip() is ""]

        babylon_dict['macros'].append(
            {
                "template": children[0].text.strip(),
                "rule": rule,
                "public": False if children[0].text.strip().startswith('-') else True,
            }
        )

    return babylon_dict


def datetime_to_hours_and_minutes(dt):
    """
    Function to convert a datetime back to the HH:MM am that Rubble
    needs to work with
    :param dt:
    :return:
    """
    return dt.strftime('%I:%M %p').lower()


def to_python_template(babylon_string):
    """
    Convert a babylon template string into a python template string
    :param babylon_string:
    :return:
    """
    # remove the asterisk, python matches on type automatically
    # by default
    babylon_string = babylon_string.replace('*:', '')
    babylon_string = babylon_string.replace('{integer:hour}:{integer:minute} {period}', '{time}')
    return babylon_string


def parse_template_params(babylon_template):
    """
    Given a babylon string template parse all the available parameters
    :param string_template:
    :return:
    """
    return ""


class Babylon:

    def __init__(self, auth, config):
        self.auth = auth
        self.config = config

    def translate(self, string, macro_file, **kwargs):
        """
        Match a given string against a babylon macro file and in return receive the
        Rubble code, associated with that string. When specifying which macro_file to
        target, i.e. for babylon/todolist-macros.xml, enter "todolist-macros";
        don't include the filename suffix or path prefix.

        Query parameters

            debug=DEBUG (optional)

        If debug=1, the generated Rubble code will contain some debugging
        information in comments before each snippet of generated code. The
        default value is 0.

        The content-type of the request body must be text/plain. Example:

            Format: babylon/foo.xml

            This could be a babylon rule.

            This could be another babylon rule.

        The Format line is mandatory and specifies the macro file to use for
        translation, in this case babylon/foo.xml relative to the repository
        root of the caller's domain. Each babylon rule is then separated from
        the preceding content via one or more empty lines. Whitespace within a
        rule will be collapsed into single spaces. Rule content is case
        insensitive unless the macro file specifies case sensitivity.

        The response always has content-type text/plain. It consists of the
        translated Rubble code. It is not stored anywhere automatically, this
        must be done as a separate operation.

        Note: to specify a macro file in some other domain, simply prepend
        /NAME/ to the Format path, where NAME is the name of the other domain.
        :param kwargs:
        :return:
        """
        params = {}
        params.update(kwargs)

        url = urljoin(self.config['url']['api'], 'babylon-translate')

        data = """Format: babylon/{macro_file}.xml

        {string}
        """.format(macro_file=macro_file, string=string)

        request_kwargs = copy.deepcopy(self.config['default_request_kwargs'])
        request_kwargs['headers']['content-type'] = "text/plain"

        request = requests.post(url,
                                auth=self.auth,
                                data=data,
                                params=params,
                                **request_kwargs)

        if not request.ok:
            raise RubbleServerException(error_string_from_request(request))

        if request.text.find("TRANSLATION ERROR") is not -1:
            print("No template match this input: {}".format(string),
                  file=sys.stderr)

        return request.text
