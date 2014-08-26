import re
import math
from datetime import datetime

KEYWORD_ENTRY_RUNNING = 'running'
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_SPEC_RE = "((?:\d{4})-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}|running)"
ENTRY_MATCHER_RE = DATE_SPEC_RE + '\s+' + DATE_SPEC_RE + '(?::?$|:\s+(.*))'
ENTRY_MATCHER = re.compile(ENTRY_MATCHER_RE)

split_words = re.compile('\s+').split

def dumps_date(d):
    """
    Encodes the given datetime object for usage in the internal
    representation.

    @param datetime.datetime d
    @return str
    """
    return d.strftime(DATE_FORMAT)

def loads_date(d):
    """
    Decodes a datetime object from the given internal string
    representation

    @param str d
    """
    return datetime.strptime(d, DATE_FORMAT)

def format_date(d):
    """
    Formats the given datetime object for better human readability

    @param datetime.datetime d
    @return str
    """
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
    """
    Formats the given timedelta object for good human readability

    @param timedelta d
    @return str
    """
    seconds = d.seconds
    minutes = math.floor(seconds / 60.)
    seconds -= minutes * 60
    hours = math.floor(minutes / 60.)
    minutes -= hours * 60

    ret = ""
    if hours == 1:
        ret += "one hour "
    elif hours > 1:
        ret += "%d hours " % hours

    if minutes:
        ret += "%d min " % minutes

    if seconds or not ret:
        ret += "%d sec " % seconds

    return ret.strip()


class LoadError(RuntimeError): pass

class Entry(object):
    """
    Entry is a single entity (i.e. one activity) with start and end time,
    optionally some text (containing +Foo tags) and an optional id
    (passed externally).
    """
    def __init__(self, text='', id=None):
        self.id = id
        self.text = text
        self.start = datetime.now()
        self.end = None

    @property
    def duration(self):
        return self.end - self.start

    def format(self):
        """
        Formats this Entry for easy human readability

        @return str
        """
        ret = "Task %s, " % (self.id or '?')
        ret += "started %s, " % format_date(self.start)
        if self.end:
            ret += "finished %s" % format_date(self.end)
            ret += " (%s)" % format_timedelta(self.duration)
        else:
            ret += "until now"
        ret += ": %s" % (self.text or '(no text)')
        return ret

    def dumps(self):
        """
        Encodes this Entry for storage in a database

        @return str
        """
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
        """
        Creates a new entry from the given string representation
        (e.g. from a database). Optionally an id can be set.
        """
        m = ENTRY_MATCHER.match(s)
        if not m:
            raise LoadError("unable to parse the entry")
        e = cls(id=id)
        e.start = loads_date(m.group(1))
        if m.group(2) != KEYWORD_ENTRY_RUNNING:
            e.end = loads_date(m.group(2))
        e.text = m.group(3) or ''
        return e

    def get_tags(self):
        """
        Returns a set of all tags which this Entry is associated with.

        @return set
        """
        tags = set()
        for word in split_words(self.text):
            if not word.startswith('+') or not word[1:]:
                continue
            tags.add(word[1:].lower())

        return tags
