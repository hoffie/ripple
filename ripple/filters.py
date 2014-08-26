import re
from functools import partial
from datetime import date, datetime, timedelta

all_entries = lambda entries: entries
DATE_RE = r"^\d{4}-\d{1,2}-\d{1,2}\Z"
is_date = re.compile(DATE_RE).match
is_year = re.compile(r'^\d{4}\Z').match
is_year_and_month = re.compile(r'^\d{4}-\d{1,2}\Z').match
is_timeframe = re.compile(
    r'^\d{4}-\d{1,2}-\d{1,2}\.\.\d{4}-\d{1,2}-\d{1,2}\Z').match
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
        elif arg == '@yesterday':
            dates.add(date.today() - timedelta(days=1))
        elif arg[0] == '@' and is_date(arg[1:]):
            try:
                d = datetime.strptime(arg[1:], DATE_FORMAT).date()
            except Exception:
                raise InvalidDateError(
                    "unable to parse the given date %s" % arg[1:])
            dates.add(d)
        else:
            remaining_args.append(arg)

    if dates:
        filter = partial(get_entries_with_dates, dates)
    else:
        filter = all_entries
    return filter, remaining_args

def get_last_day_of_month(d):
    if d.month == 12:
        d = d.replace(year=d.year + 1, month=1, day=1)
    else:
        d = d.replace(month=d.month + 1, day=1)
    d -= timedelta(days=1)
    return d

def build_timeframe_filter(args):
    remaining_args = []
    timeframes = set()
    today = date.today()
    for arg in args:
        if arg == '@week':
            first_day = today - timedelta(days=today.weekday())
            last_day = first_day + timedelta(days=7)
        elif arg == '@month':
            first_day = today.replace(day=1)
            last_day = get_last_day_of_month(first_day)
        elif arg == '@year':
            first_day = today.replace(month=1, day=1)
            last_day = today.replace(month=12, day=31)
        elif arg.startswith('@') and is_year(arg[1:]):
            first_day = date(year=int(arg[1:]), month=1, day=1)
            last_day = first_day.replace(month=12, day=31)
        elif arg.startswith('@') and is_year_and_month(arg[1:]):
            try:
                d = datetime.strptime(arg[1:], '%Y-%m').date()
            except ValueError:
                raise InvalidDateError("unable to parse %s" % arg[1:])
            first_day = d
            last_day = get_last_day_of_month(first_day)
        elif arg.startswith('@') and is_timeframe(arg[1:]):
            a, b = arg[1:].split('..', 1)
            try:
                first_day = datetime.strptime(a, DATE_FORMAT).date()
            except ValueError:
                raise InvalidDateError("unable to parse %s" % a)
            try:
                last_day = datetime.strptime(b, DATE_FORMAT).date()
            except ValueError:
                raise InvalidDateError("unable to parse %s" % b)
        else:
            remaining_args.append(arg)
            continue
        timeframes.add((first_day, last_day))

    if timeframes:
        filter = partial(get_entries_within_timeframes, timeframes)
    else:
        filter = all_entries
    print timeframes
    return filter, remaining_args

def get_entries_within_timeframes(timeframes, entries):
    for entry in entries:
        for timeframe in timeframes:
            if (timeframe[0] <= entry.start.date() <= timeframe[1] or
                (entry.end and timeframe[0] <= entry.end.date() <= timeframe[1])):
                yield entry


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
