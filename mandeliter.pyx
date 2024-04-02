#!python
#cython: language_level=3

import cython
import parameters as P
from numpy import exp, log
import sys

growthCounter = 0

# The color map is used for caching color codes assigned
colorCodeMap = {}
def resetColorMap ():
    colorCodeMap = {}

def colorValue (counter, colorFactor, offset, cs):
    counter = counter - offset
    if counter < 1:
        counter = 1
    return ((log(counter)**cs)/10)*1j*exp(-1j*counter*colorFactor)/P.COLORDAMPENING   

def colorCode (counter, useCache, colorFactor, offset, cs):
    # global P.COLORSTEEPNESS
    retVal = 0
    if useCache:
        try:
            # See if a cached result is available
            retVal = colorCodeMap [counter]
            return retVal
        except KeyError:
            # No color code found in cache. Compute a new one. 
            retVal = colorValue (counter, colorFactor, offset, cs)
            # Cache the result
            colorCodeMap [counter] = retVal
            return retVal
    else:
        return colorValue (counter, colorFactor, offset, cs)


def printOut (s):
    sys.stdout.write (".")
    sys.stdout.flush ()    

def reportGrowth ():
    # Show progress
    global growthCounter
    growthCounter += 1
    if growthCounter % 10000 == 0:
        printOut (".")
 
def growth (c, colorFactor, nrOfIterations, offset, cs) -> int :
	
    # This is the iteration used to find convergence, looping or divergence
    # Escape count can be calculated for divergence
    cdef double complex result    = 0.0
    cdef double absResult         = 1.0
    cdef double absDiffResult     = 1.0
    cdef double complex newResult = 0.0
    cdef double newAbsDiffResult  = 0.0
    cdef double newAbsResult      = 0.0

    if abs(c) <= 0.25:
        # No need to iterate here. It will converge.
        reportGrowth ()
        return 0

    for i in range (0,nrOfIterations):
        newResult = result*result + c
        newAbsDiffResult  = abs(newResult - result)
        newAbsResult      = abs(newResult)
        # print (newAbsResult) # TODO Remove
        if newAbsDiffResult < P.CONVERGENCE_LIMIT:
            # Convergence found
            reportGrowth ()
            if P.DEBUG:
                printOut ("S")
            # Assign zero = convergence = Black color
            return 0
        elif newAbsResult > P.DIVERGENCE_LIMIT:
            # Divergence found. Find escape count and assign color.
            reportGrowth ()
            if P.DEBUG: 
                printOut ("E")
            if P.PARTIALESCAPECOUNT:
                ratio = log(P.DIVERGENCE_LIMIT/absResult) / log(newAbsResult/absResult)
                return colorCode (i + 1.5 + ratio, False, colorFactor, offset, cs)
            else:
                return colorCode (i + 1, True, colorFactor, offset, cs)
        result = newResult
        absDiffResult = newAbsDiffResult
        absResult     = newAbsResult
    # Search exhausted. Assume looping.
    reportGrowth ()
    if P.DEBUG:
        printOut ("!")
    return 0    
