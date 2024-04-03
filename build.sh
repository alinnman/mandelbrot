 #!/bin/bash

PY_SCRIPT="from sysconfig import get_paths
import sys
from pprint import pprint
info = get_paths()
sys.stdout.write(info['include'])
"
INCLUDEPATH=`python -c "$PY_SCRIPT"`
cython -a mandeliter.pyx
gcc -shared -pthread -fPIC -fwrapv -O2 -Wall -fno-strict-aliasing -I$INCLUDEPATH -o mandeliter.so mandeliter.c

