from functools import partial
from datetime import date, timedelta

all_entries = lambda entries: entries

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
