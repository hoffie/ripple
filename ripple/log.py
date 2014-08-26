import sys

def abort(s):
    """
    Writes the given error message to stderr and
    exits with a failure code.

    @param str s
    """
    sys.stderr.write("error: %s\n" % s)
    sys.exit(1)

def warn(s):
    """
    Writes the given warning message to stderr.

    @param str
    """
    sys.stderr.write("warning: %s\n" % s)
