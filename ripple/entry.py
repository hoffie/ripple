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
    return d.strftime(DATE_FORMAT)

def loads_date(d):
    return datetime.strptime(d, DATE_FORMAT)

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


class LoadError(RuntimeError): pass

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
            raise LoadError("unable to parse the entry")
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
