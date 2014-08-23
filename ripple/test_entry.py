import unittest
from datetime import datetime
from .entry import Entry

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
        self.assertEquals(e.dumps(), "2014-08-22 17:10:00 running: foobar +uni")
        self.assertEquals(e.get_tags(), {"uni"})
