import sys

def abort(s):
    sys.stderr.write("error: %s\n" % s)
    sys.exit(1)

def warn(s):
    sys.stderr.write("warning: %s\n" % s)
