import os
from .log import warn
from .entry import Entry, LoadError

DB_FILE_DEFAULT = os.path.expanduser(os.path.join("~", ".ripple.txt"))
DB_FILE = os.environ.get('RIPPLE_DB', DB_FILE_DEFAULT)
DB_TMP_FILE = DB_FILE + '.tmp'

def get_db():
    if os.path.isfile(DB_FILE):
        with open(DB_FILE, 'r+') as handle:
            return DB.load(handle)
    return DB()

def save_db(db):
    with open(DB_TMP_FILE, 'w') as handle:
        db.dump(handle)
    os.rename(DB_TMP_FILE, DB_FILE)

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
            try:
                entry = Entry.loads(line.strip(), id=x)
            except LoadError:
                warn("unable to parse a line!")
                continue
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
