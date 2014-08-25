import re
from functools import partial
from datetime import date, datetime, timedelta

all_entries = lambda entries: entries
DATE_RE = r"^\d{4}-\d{1,2}-\d{1,2}\Z"
is_date = re.compile(DATE_RE).match
DATE_FORMAT = "%Y-%m-%d"

class InvalidDateError(RuntimeError): pass

def build_tag_filter(args):
    remaining_args = []
    tags = set()
    for arg in args:
        if arg.startswith('+'):
            tags.add(arg[1:])
        else:
            remaining_args.append(arg)

    filter = partial(get_entries_with_tags, tags)
    return filter, remaining_args

def build_date_filter(args):
    remaining_args = []
    dates = set()
    for arg in args:
        if arg == '@today':
            dates.add(date.today())
            continue
        elif arg == '@yesterday':
            dates.add(date.today() - timedelta(days=1))
        elif arg[0] == '@' and is_date(arg[1:]):
            try:
                d = datetime.strptime(arg[1:], DATE_FORMAT).date()
            except Exception:
                raise InvalidDateError(
                    "unable to parse the given date %s" % arg[1:])
            dates.add(d)
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

def get_entries_with_tags(tags, entries):
    """
    Returns all entries which match all of the given tags.

    @param iterable tags
    @return generator[Entry]
    """
    for entry in entries:
        skip = False
        for wanted_tag in tags:
            if wanted_tag.lower() not in entry.get_tags():
                skip = True
                break
        if not skip:
            yield entry
