import os
from .db import get_db, save_db, DB_FILE
from .entry import Entry
from .log import abort
from subprocess import call
from datetime import datetime

EDITOR = os.environ.get('EDITOR', 'vim')

def help(args):
    print("""Usage: ripple.py COMMAND
    start
    stop
    list
    edit
""")

def track(args):
    db = get_db()
    for entry in db.get_running_entries():
        print("note: finishing running entry:")
        print("\t%s" % entry.format())
        entry.end = datetime.now()

    entry = Entry(text=' '.join(args))
    db.append(entry)
    save_db(db)

def end(args):
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

def ls(args):
    db = get_db()
    tags = []
    for arg in args:
        if arg.startswith('+'):
            tags.append(arg[1:])
        else:
            tags.append(arg)

    entries = db.get_entries_with_tags(*tags)

    for entry in entries:
        print(entry.format())

def edit(args):
    call([EDITOR, DB_FILE])

def dispatch(args):
    f = unknown
    if not args or args[0] in ('ls', 'list'):
        f = ls
    elif args[0] in ('on', 'in', 'start', 'track'):
        f = track
    elif args[0] in ('end', 'out', 'stop', 'done'):
        f = end
    elif args[0] in ('edit',):
        f = edit
    elif args[0] in ('help', '?'):
        f = help
    return f(args[1:])

def unknown(args):
    abort("unknown command")
