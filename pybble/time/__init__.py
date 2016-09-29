import datetime


def now():
    """Get now as microseconds since the UNIX epoch.
    """
    return int(datetime.datetime.now().strftime("%s")) * 1000


def datetime_to_epoch(datetime_obj):
    """Get now as microseconds since the UNIX epoch.
    """
    return int(datetime_obj.strftime("%s")) * 1000