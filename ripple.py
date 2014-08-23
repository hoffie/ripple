#!/usr/bin/env python
import sys
from ripple.cli import dispatch

if __name__ == '__main__':
    dispatch(sys.argv[1:])
