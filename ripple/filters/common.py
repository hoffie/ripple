from datetime import datetime

"""
Full date format
"""
DATE_FORMAT = "%Y-%m-%d"

class InvalidDateError(RuntimeError):
    """
    InvalidDateError is thrown whenever an unparsable is encountered
    """

def parse_date(val, format):
    """
    Attempts to parse the given string date according to the
    provided format, raising InvalidDateError in case of problems.

    @param str val (e.g. 2014-08-12)
    @param str format (e.g. %Y-%m-%d)
    @return datetime.date
    """
    try:
        return datetime.strptime(val, format).date()
    except ValueError:
        raise InvalidDateError("unable to parse %s" % val)

"""
Special filter which returns all entries.
"""
all_entries = lambda entries: entries
