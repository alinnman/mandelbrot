#!python
#cython: language_level=3

import sys
from libc.math cimport log as c_log, sin as c_sin, cos as c_cos, exp as c_exp
#from libc.complex cimport creal as c_real, cimag as c_imag
import cython

cdef int growthCounter = 0

# The color map is used for caching color codes assigned
cdef colorCodeMap = {}
def resetColorMap ():
    global colorCodeMap
    colorCodeMap = {}
    
cdef double complex complex_exp (double complex val) :
    cdef double         aPart = c_exp (val.real)
    cdef double complex bPart = c_cos (val.imag) + 1j * c_sin (val.imag)
    return aPart * bPart

cdef double complex colorValue (counter, colorFactor, offset, cs, cd):
    cdef double c_counter = counter
    cdef double c_colorFactor = colorFactor
    cdef double c_offset = offset
    cdef double c_cs = cs
    cdef double c_cd = cd
    
    c_counter = c_counter - c_offset
    if c_counter < 1:
        c_counter = 1
    return ((c_log(c_counter)**c_cs)/10)*1j*complex_exp(-1j*c_counter*c_colorFactor)/c_cd    

cdef double complex colorCode (counter, useCache, colorFactor, offset, cs, cd):
    # global P.COLORSTEEPNESS
    global colorCodeMap
    retVal = 0
    if useCache:
        try:
            # See if a cached result is available
            retVal = colorCodeMap [counter]
            return retVal
        except KeyError:
            # No color code found in cache. Compute a new one. 
            retVal = colorValue (counter, colorFactor, offset, cs, cd)
            # Cache the result
            colorCodeMap [counter] = retVal
            return retVal
    else:
        return colorValue (counter, colorFactor, offset, cs, cd)


cdef printOut (s):
    sys.stdout.write (s)
    sys.stdout.flush ()    

cdef reportGrowth (index):
    # Show progress
    global growthCounter
    growthCounter += 1
    if growthCounter % 10000 == 0:
        printOut (str(index))
 
def growth (c, colorFactor, nrOfIterations, offset, cs, pe, cl, dl, debug, cd, index) :
	
    # This is the iteration used to find convergence, looping or divergence
    # Escape count can be calculated for divergence
    
    # The code is optimized using Cython 
    
    cdef double complex cc        = c
    cdef double complex result    = 0.0
    cdef double absResult         = 1.0
    cdef double absDiffResult     = 1.0
    cdef double complex newResult = 0.0
    cdef double newAbsDiffResult  = 0.0
    cdef double newAbsResult      = 0.0
    cdef double conv_limit        = cl
    cdef double conv_limit2       = conv_limit * conv_limit
    cdef double div_limit         = dl
    cdef double div_limit2        = div_limit  * div_limit
    cdef int    i                 = 0
    cdef int    nrIt              = nrOfIterations
    cdef double X1                = 0.0
    cdef double X2                = 0.0

    #if abs(cc) <= 0.25:
    #    # No need to iterate here. It will converge.
    #    reportGrowth ()
    #    return 0

    while i < nrIt: 
        newResult        = result*result    +cc
        X1               = newResult.real-result.real
        X2               = newResult.imag-result.imag
        newAbsDiffResult = X1*X1            +X2*X2
        newAbsResult     = newResult.real*newResult.real +\
                           newResult.imag*newResult.imag
        if newAbsDiffResult < conv_limit2:
            # Convergence found
            reportGrowth (index)
            if debug:
                printOut ("S")
            # Assign zero = convergence = Black color
            return 0
        elif newAbsResult > div_limit2:
            # Divergence found. Find escape count and assign color.
            reportGrowth (index)
            if debug: 
                printOut ("E")
            if pe:
                X1 = c_log(div_limit2/absResult) / c_log(newAbsResult/absResult)
                return colorCode (i + 1.5 + X1, False, colorFactor, offset, cs, cd)
            else:
                return colorCode (i + 1, True, colorFactor, offset, cs, cd)
        result = newResult
        absDiffResult = newAbsDiffResult
        absResult     = newAbsResult
        i             = i+1
    # Search exhausted. Assume looping.
    reportGrowth (index)
    if debug:
        printOut ("!")
    return 0


