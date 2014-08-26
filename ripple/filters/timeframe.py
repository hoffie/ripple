import re
from functools import partial
from datetime import date, datetime, timedelta
from .common import InvalidDateError, DATE_FORMAT, all_entries

is_year = re.compile(r'^\d{4}\Z').match
is_year_and_month = re.compile(r'^\d{4}-\d{1,2}\Z').match
is_timeframe = re.compile(
    r'^\d{4}-\d{1,2}-\d{1,2}\.\.\d{4}-\d{1,2}-\d{1,2}\Z').match

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
    return filter, remaining_args

def get_entries_within_timeframes(timeframes, entries):
    return [entry for entry in entries
        if entry_is_within_timeframes(entry, timeframes)]

def entry_is_within_timeframes(entry, timeframes):
    for start, end in timeframes:
        if (start <= entry.start.date() <= end or
            (entry.end and start <= entry.end.date() <= end)):
            return True
    return False
