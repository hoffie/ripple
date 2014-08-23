import unittest
from datetime import datetime, timedelta
from .entry import (Entry, dumps_date, loads_date, format_date,
    format_timedelta)

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
        e = Entry(text="foobar +Uni")
        e.start = datetime(2014, 8, 22, 17, 10)
        self.assertEquals(e.dumps(), "2014-08-22 17:10:00 running: foobar +Uni")
        self.assertEquals(e.get_tags(), {"uni"})


class TestHelpers(unittest.TestCase):
    def test_dumps_date(self):
        d = datetime(2014, 8, 22, 17, 10)
        self.assertEquals(dumps_date(d), "2014-08-22 17:10:00")

    def test_loads_date(self):
        d = datetime(2014, 8, 22, 17, 10)
        self.assertEquals(loads_date(dumps_date(d)), d)

    def test_format_date_today(self):
        d = datetime.now()
        d = d.replace(hour=0, minute=0, second=0)
        self.assertEquals(format_date(d), "today 00:00")

    def test_format_date_yesterday(self):
        d = datetime.now() - timedelta(days=1)
        d = d.replace(hour=0, minute=0, second=0)
        self.assertEquals(format_date(d), "yesterday 00:00")

    def test_format_date_3_days(self):
        d = datetime.now() - timedelta(days=3)
        d = d.replace(hour=0, minute=0, second=0)
        self.assertEquals(format_date(d), "3 days ago 00:00")

    def test_format_date_absolute(self):
        d = datetime(2014, 8, 1, 0, 0, 0)
        self.assertEquals(format_date(d), "2014-08-01 00:00")

    def test_format_timedelta_sec(self):
        d = timedelta(seconds=3)
        self.assertEquals(format_timedelta(d), "3 sec")

    def test_format_timedelta_min(self):
        d = timedelta(seconds=61)
        self.assertEquals(format_timedelta(d), "1 min 1 sec")

    def test_format_timedelta_hour(self):
        d = timedelta(seconds=3600)
        self.assertEquals(format_timedelta(d), "one hour")

    def test_format_timedelta_hours(self):
        d = timedelta(seconds=7777)
        self.assertEquals(format_timedelta(d), "2 hours 9 min 37 sec")

