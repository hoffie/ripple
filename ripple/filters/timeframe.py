import re
from functools import partial
from datetime import date, timedelta
from .common import DATE_FORMAT, all_entries, parse_date

is_year = re.compile(r'^\d{4}\Z').match
is_year_and_month = re.compile(r'^\d{4}-\d{1,2}\Z').match
is_timeframe = re.compile(
    r'^\d{4}-\d{1,2}-\d{1,2}\.\.\d{4}-\d{1,2}-\d{1,2}\Z').match

def get_last_day_of_month(d):
    """
    Takes a date object and returns another date object of the
    last day of the same month.

    @param datetime.date d
    @return datetime.date
    """
    if d.month == 12:
        d = d.replace(year=d.year + 1, month=1, day=1)
    else:
        d = d.replace(month=d.month + 1, day=1)
    d -= timedelta(days=1)
    return d

def build_timeframe_filter(args):
    """
    Returns a filter which selects entries within the given
    time frames only.

    @param list(str) args, e.g. ["@week", "@month", "@year", "unrelated"]
    @return (callable filter, list remaining_args)
    """
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
            first_day = parse_date(arg[1:], '%Y-%m')
            last_day = get_last_day_of_month(first_day)

        elif arg.startswith('@') and is_timeframe(arg[1:]):
            a, b = arg[1:].split('..', 1)
            first_day = parse_date(a, DATE_FORMAT)
            last_day = parse_date(b, DATE_FORMAT)

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
    """
    Returns all entries which are within one of the given
    timeframes.

    @param set((start, end)) timeframes
    @param iterable entries
    @return generator[Entry]
    """
    return [entry for entry in entries
        if entry_is_within_timeframes(entry, timeframes)]

def entry_is_within_timeframes(entry, timeframes):
    """
    Returns whether the given entry is within one of the
    given time frames.

    @param Entry entry
    @param set((start, end)) timeframes
    @return bool
    """
    for start, end in timeframes:
        if (start <= entry.start.date() <= end or
            (entry.end and start <= entry.end.date() <= end)):
            return True
    return False
