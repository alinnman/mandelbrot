from distutils.core import setup
from distutils.extension import Extension

from Cython.Distutils import build_ext

from time import time

time1 = time()

setup(\
        cmdclass = {'build_ext': build_ext},\
        ext_modules = [Extension("mandeliter",\
    ["mandeliter.pyx"])] )
    
time2 = time()
timeDiff = time2 - time1
print ("Build took " + str(round(timeDiff,2)))
