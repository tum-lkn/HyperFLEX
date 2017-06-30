#!/bin/python
import os
import sys

path = os.path.dirname(os.path.realpath(sys.argv[0]))
slash_idx = path.rfind(os.path.sep)
print path[0:slash_idx + 1]
sys.path.insert(1, path[0:slash_idx + 1])
