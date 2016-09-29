
class RubbleServerException(Exception):
    pass


def error_string_from_request(request):
    """
    Format an error string from a Request object
    :param request:
    :type request:
        :class:`Request`
    :return:
    """
    return "{status_code} {reason}".format(
        status_code=request.status_code,
        reason=request.reason,
    )
