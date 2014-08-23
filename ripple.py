#!/usr/bin/env python
import os
import sys
import re
import math
import unittest
from subprocess import call
from datetime import datetime

DB_FILE_DEFAULT = os.path.expanduser(os.path.join("~", ".ripple.txt"))
DB_FILE = os.environ.get('RIPPLE_DB', DB_FILE_DEFAULT)
DB_TMP_FILE = DB_FILE + '.tmp'
DB_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

DATE_SPEC_RE = "((?:\d{4})-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}|running)"
ENTRY_MATCHER_RE = DATE_SPEC_RE + '\s+' + DATE_SPEC_RE + '(?::?$|:\s+(.*))'
ENTRY_MATCHER = re.compile(ENTRY_MATCHER_RE)

EDITOR = os.environ.get('EDITOR', 'vim')

KEYWORD_ENTRY_RUNNING = 'running'
HOURS = 3600

split_words = re.compile('\s+').split

def dumps_date(d):
    return d.strftime(DB_DATE_FORMAT)

def loads_date(d):
    return datetime.strptime(d, DB_DATE_FORMAT)

def format_date(d):
    age = datetime.now().date() - d.date()
    date = d.strftime("%Y-%m-%d")
    if age.days == 0:
        date = 'today'
    elif age.days == 1:
        date = 'yesterday'
    elif age.days < 6:
        date = '%d days ago' % age.days

    time = d.strftime("%H:%M")
    return "%s %s" % (date, time)

def format_timedelta(d):
    seconds = d.seconds
    minutes = math.floor(seconds / 60.)
    seconds -= minutes * 60
    hours = math.floor(seconds / 60.)
    seconds -= hours * 60

    ret = ""
    if hours == 1:
        ret += "one hour "
    elif hours > 1:
        ret += "%d hours " % hours

    if minutes:
        ret += "%d min " % minutes

    if seconds:
        ret += "%d sec " % seconds

    return ret.strip()


class Entry(object):
    def __init__(self, text='', id=None):
        self.id = id
        self.text = text
        self.start = datetime.now()
        self.end = None

    def format(self):
        ret = "Task %s, " % (self.id or '?')
        ret += "started %s, " % format_date(self.start)
        if self.end:
            ret += "finished %s" % format_date(self.end)
            duration = self.end - self.start
            ret += " (%s)" % format_timedelta(duration)
        else:
            ret += "until now"
        ret += ": %s" % (self.text or '(no text)')
        return ret

    def dumps(self):
        start = dumps_date(self.start)
        if self.end:
            end = dumps_date(self.end)
        else:
            end = KEYWORD_ENTRY_RUNNING

        ret = "%s %s: %s" % (
            start,
            end,
            self.text)
        return ret

    @classmethod
    def loads(cls, s, id=None):
        m = ENTRY_MATCHER.match(s)
        if not m:
            warn("unable to parse a line!")
            return
        e = cls(id=id)
        e.start = loads_date(m.group(1))
        if m.group(2) != KEYWORD_ENTRY_RUNNING:
            e.end = loads_date(m.group(2))
        e.text = m.group(3) or ''
        return e

    def get_tags(self):
        tags = set()
        for word in split_words(self.text):
            if not word.startswith('+') or not word[1:]:
                continue
            tags.add(word[1:].lower())

        return tags


class DB(object):
    def __init__(self):
        self.entries = []

    def append(self, entry):
        self.entries.append(entry)

    def dump(self, writer):
        for entry in self.entries:
            writer.write(entry.dumps())
            writer.write("\n")

    @classmethod
    def load(cls, iterable):
        x = 1
        db = DB()
        for line in iterable:
            if not line.strip() or line[0] == '#':
                continue
            entry = Entry.loads(line.strip(), id=x)
            if entry:
                db.entries.append(entry)
                x += 1
        return db

    def get_running_entries(self):
        for entry in self.entries:
            if not entry.end:
                yield entry

    def get_most_recent_entry(self):
        if self.entries:
            return self.entries[-1]
        return None

    def get_entries_with_tags(self, *tags):
        for entry in self.entries:
            skip = False
            for wanted_tag in tags:
                if wanted_tag.lower() not in entry.get_tags():
                    skip = True
                    break
            if not skip:
                yield entry

def abort(s):
    sys.stderr.write("error: %s\n" % s)
    sys.exit(1)

def warn(s):
    sys.stderr.write("warning: %s\n" % s)

def unknown(args):
    abort("unknown command")

def help(args):
    print("""Usage: ripple.py COMMAND
    start
    stop
    list
    edit
""")

def get_db():
    if os.path.isfile(DB_FILE):
        with open(DB_FILE, 'r+') as handle:
            return DB.load(handle)
    return DB()

def save_db(db):
    with open(DB_TMP_FILE, 'w') as handle:
        db.dump(handle)
    os.rename(DB_TMP_FILE, DB_FILE)

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


class TestEntry(unittest.TestCase):
    def test_default(self):
        e = Entry()
        e.start = datetime(2014, 8, 22, 17, 10)
        self.assertEquals(e.dumps(), "2014-08-22 17:10:00 running: ")

    def test_text(self):
        e = Entry(text="foobar")
        e.start = datetime(2014, 8, 22, 17, 10)
        self.assertEquals(e.dumps(), "2014-08-22 17:10:00 running: foobar")

    def test_get_tags(self):
        e = Entry(text="foobar +uni")
        e.start = datetime(2014, 8, 22, 17, 10)
        self.assertEquals(e.dumps(), "2014-08-22 17:10:00 running: foobar +Uni")
        self.assertEquals(e.get_tags(), {"uni"})


if __name__ == '__main__':
    dispatch(sys.argv[1:])
