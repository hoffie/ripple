import os
from .log import warn
from .entry import Entry, LoadError

DB_FILE_DEFAULT = os.path.expanduser(os.path.join("~", ".ripple.txt"))
DB_FILE = os.path.realpath(os.environ.get('RIPPLE_DB', DB_FILE_DEFAULT))
DB_TMP_FILE = DB_FILE + '.tmp'

def get_db():
    """
    Opens the database file and returns the resulting instance.
    """
    if os.path.isfile(DB_FILE):
        with open(DB_FILE, 'r+') as handle:
            return DB.load(handle)
    return DB()

def save_db(db):
    """
    Saves the database to disk
    """
    with open(DB_TMP_FILE, 'w') as handle:
        db.dump(handle)
    os.rename(DB_TMP_FILE, DB_FILE)

class DB(object):
    """
    The database of all entries.

    Nothing fancy for now, everything in-memory, so you should probably
    archive entries at some point.
    """
    def __init__(self):
        self.entries = []

    def append(self, entry):
        """
        Adds the given entry at the end of the database.

        @param Entry entry
        """
        self.entries.append(entry)

    def dump(self, writer):
        """
        Encodes the state into text format and writes it
        to the given writer.

        @param [.write(str)-supporting object] writer
        """
        for entry in self.entries:
            writer.write(entry.dumps())
            writer.write("\n")

    @classmethod
    def load(cls, iterable):
        """
        Creates a new DB instance, pre-populated with the parseable
        entries.

        @param iterable iterable (usually emitting lines)
        """
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

    def get_entries(self):
        """
        Returns an iterator over all entries
        """
        return self.entries

    def get_unfinished_entries(self):
        """
        Returns a generator over all entries which have not been
        finished yet. Usually this should only be one entry.

        @return generator
        """
        for entry in self.entries:
            if not entry.end:
                yield entry

    def get_most_recent_entry(self):
        """
        Returns the most-recently added entry.

        @return Entry
        """
        if self.entries:
            return self.entries[-1]
        return None
