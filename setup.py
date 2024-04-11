from distutils.core import setup
from distutils.extension import Extension

from Cython.Distutils import build_ext
from time import time

time1 = time ()

from time import time

time1 = time()

setup(\
        cmdclass = {'build_ext': build_ext},\
        ext_modules = [Extension("mandeliter",\
    ["mandeliter.pyx"])] )
    
<<<<<<< Updated upstream
time2 = time()
timeDiff = time2 - time1
print ("Build took " + str(round(timeDiff,2)))
=======
time2 = time ()
timeTaken = time2 - time1
print ("Time taken = " + str(round (timeTaken, 2)))
>>>>>>> Stashed changes
