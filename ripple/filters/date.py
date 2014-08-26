import re
from functools import partial
from datetime import date, timedelta
from .common import all_entries, parse_date, DATE_FORMAT

DATE_RE = r"^\d{4}-\d{1,2}-\d{1,2}\Z"
is_date = re.compile(DATE_RE).match

def build_date_filter(args):
    remaining_args = []
    dates = set()
    for arg in args:
        if arg == '@today':
            dates.add(date.today())
        elif arg == '@yesterday':
            dates.add(date.today() - timedelta(days=1))
        elif arg[0] == '@' and is_date(arg[1:]):
            d = parse_date(arg[1:], DATE_FORMAT)
            dates.add(d)
        else:
            remaining_args.append(arg)

    if dates:
        filter = partial(get_entries_with_dates, dates)
    else:
        filter = all_entries
    return filter, remaining_args


def get_entries_with_dates(dates, entries):
    for entry in entries:
        if (entry.start.date() in dates or
            entry.end and entry.end.date() in dates):
            yield entry
