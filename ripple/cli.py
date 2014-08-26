# The cli module contains all commands which are supported by the
# command line interface. dispatch() is the entry point which selects the
# proper method.
import os
from .db import get_db, save_db, DB_FILE
from .entry import Entry, format_timedelta
from .filters import (build_tag_filter, build_date_filter,
    build_timeframe_filter)
from .log import abort, warn
from subprocess import call
from datetime import datetime, timedelta

EDITOR = os.environ.get('EDITOR', 'vim')

def help(args):
    print("""Usage: ripple.py COMMAND
    start
    stop
    list
    edit
""")

def start_tracking(args):
    db = get_db()
    for entry in db.get_unfinished_entries():
        print("note: ending unfinished entry:")
        print("\t%s" % entry.format())
        entry.end = datetime.now()

    entry = Entry(text=' '.join(args))
    db.append(entry)
    save_db(db)

def stop_tracking(args):
    db = get_db()
    entry = db.get_most_recent_entry()
    if not entry:
        abort("nothing to end (no previous entries found)")
    if entry.end:
        abort("nothing to end!")
    entry.end = datetime.now()
    if args:
        entry.text = (entry.text + ' '.join(args)).strip()
    save_db(db)

def list_entries(args):
    db = get_db()
    tags = []
    tag_filter, args = build_tag_filter(args)
    date_filter, args = build_date_filter(args)
    timeframe_filter, args = build_timeframe_filter(args)
    if args:
        warn("the following arguments have not been considered: %s" % args)

    entries = db.get_entries()
    entries = tag_filter(entries)
    entries = date_filter(entries)
    entries = timeframe_filter(entries)

    duration = timedelta(seconds=0)

    for entry in entries:
        duration += entry.duration
        print(entry.format())

    print("\nduration of all entries shown: %s" %
        format_timedelta(duration))

def open_in_editor(args):
    call([EDITOR, DB_FILE])

def dispatch(args):
    f = unknown_command
    if not args or args[0] in ('ls', 'list'):
        f = list_entries
    elif args[0] in ('on', 'in', 'start', 'track'):
        f = start_tracking
    elif args[0] in ('end', 'out', 'stop', 'done'):
        f = stop_tracking
    elif args[0] in ('edit',):
        f = open_in_editor
    elif args[0] in ('help', '?'):
        f = help
    return f(args[1:])

def unknown_command(args):
    abort("unknown command")
