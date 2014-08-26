from datetime import datetime

DATE_FORMAT = "%Y-%m-%d"

class InvalidDateError(RuntimeError): pass

def parse_date(val, format):
    try:
        return datetime.strptime(val, format).date()
    except ValueError:
        raise InvalidDateError("unable to parse %s" % val)

all_entries = lambda entries: entries
