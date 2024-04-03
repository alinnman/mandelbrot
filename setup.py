from distutils.core import setup
from distutils.extension import Extension

# Execute this to get HTML file with annotations
#import subprocess
#subprocess.call(["cython","-a","mandeliter.pyx"])

from Cython.Distutils import build_ext

setup(\
        cmdclass = {'build_ext': build_ext},\
        ext_modules = [Extension("mandeliter",\
    ["mandeliter.pyx"])] )