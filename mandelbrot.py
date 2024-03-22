try:
    # Lazy from matplotlib import pyplot as plt
    from numpy import ndarray, array, log, exp, frombuffer
    from os import environ, path, makedirs, _exit
    # Lazy from time import time
    # Lazy from cplot import plot as complex_plot # NOTE: The cplot fork in my repositry https://github.com/alinnman/cplot2.git is recommended. 
    from multiprocessing import Process, Semaphore, Queue, freeze_support
    # Lazy import itertools
    from pickle import loads as ploads, dumps as pdumps
except BaseException as be: 
    print ("Interrupted while loading packages")
    raise be

DPI = 400
POWER = 2
DIAGPOINTS=500
FIGSIZE=20
ITERATIONS=1000
DEBUG=False

DIVERGENCE_LIMIT = 2
CONVERGENCE_LIMIT = 1e-6

PARALELL = False
CHUNKLENGTH = 100000
#CHUNKLENGTH = 500000
MAXRUNNINGPROCESSES = 4
PARTIALESCAPECOUNT = True
#Experimental parameters which need to be adjusted for deep zooms with small gradients
COLORSTEEPNESS = 3
COLORDAMPENING = 1

if PARALELL:
    N_THREADS = 2
    environ['OMP_NUM_THREADS'] = str(N_THREADS)
    environ['OPENBLAS_NUM_THREADS'] = str(N_THREADS)
    environ['MKL_NUM_THREADS'] = str(N_THREADS)
    environ['VECLIB_MAXIMUM_THREADS'] = str(N_THREADS)
    environ['NUMEXPR_NUM_THREADS'] = str(N_THREADS)
else:
    N_THREADS = 1

growthCounter = 0

def iter (x, c):
    global POWER
    if POWER == 2:
        # Using multiplication is a lot faster than **
        result = x*x + c
    else:
        result = x**POWER + c
    return result

# The color map is used for caching color codes assigned
colorCodeMap = {}
def resetColorMap ():
    colorCodeMap = {}
    
def colorValue (counter, colorFactor, offset):
    global COLORSTEEPNESS
    global COLORDAMPENING
    counter = counter - offset
    if counter < 0.1:
        counter = 0.1
    return ((log(counter)**(COLORSTEEPNESS))/10)*1j*exp(-1j*counter*colorFactor)/COLORDAMPENING   

def colorCode (counter, useCache, colorFactor, offset):
    global COLORSTEEPNESS
    retVal = 0
    if useCache:
        try:
            # See if a cached result is available
            retVal = colorCodeMap [counter]
            return retVal
        except:
            # No color code found in cache. Compute a new one. 
            retVal = colorValue (counter, colorFactor, offset)
            # Cache the result
            colorCodeMap [counter] = retVal
            return retVal
    else:
        return colorValue (counter, colorFactor, offset)

def reportGrowth ():
    # Show progress
    global growthCounter
    growthCounter += 1
    if growthCounter % 10000 == 0:
        print(".", end='', flush=True)

def growth (c, colorFactor, nrOfIterations, offset):
    # This is the iteration used to find convergence, looping or divergence
    # Escape count can be calculated for divergence
    counter, result, absResult, absDiffResult = 0, 0, 1, 1
    global DIVERGENCE_LIMIT
    global CONVERGENCE_LIMIT

    for i in range (0,nrOfIterations):
        counter += 1
        newResult = iter (result, c)
        diffResult = newResult - result
        newAbsDiffResult = abs(diffResult)
        newAbsResult = abs(newResult)

        if (newAbsDiffResult < CONVERGENCE_LIMIT):
            # Convergence found
            reportGrowth ()
            if DEBUG:
                print("S", end='', flush=True)
            # Assign zero = convergence = Black color
            return 0
        elif newAbsResult > DIVERGENCE_LIMIT:
            # Divergence found. Find escape count and assign color.
            reportGrowth ()
            if DEBUG:
                print("E", end='', flush=True)
            if PARTIALESCAPECOUNT:
                ratio = (log(DIVERGENCE_LIMIT) - log(absResult)) / (log(newAbsResult) - log(absResult))
                return colorCode (counter + 0.5 + ratio, False, colorFactor, offset)
            else:
                return colorCode (counter, True, colorFactor, offset)
        result = newResult
        absDiffResult = newAbsDiffResult
        absResult = newAbsResult
    # Search exhausted. Assume looping.
    reportGrowth ()
    if DEBUG:
        print("!", end='', flush=True)
    return 0

# Some test areas used.
          
COORDS = [[-2.2, 0.8,-1.3, 1.3, 2, 0],\
          [-0.4, 0.2, 0.5, 1.2, 2, 0],\
          [-0.2, -0.1, 1, 1.1, 2, 0],\
          [-0.184, -0.16, 1.06, 1.08, 2, 0],\
          [-0.176, -0.1725, 1.07, 1.073, 2, 0],\
          [-0.5625, -0.5476, -0.6300, -0.6165, 2.5, 0],\
          [-0.74453892-1e-4,-0.74453892+1e-4,0.12172418-1e-4,0.12172418+1e-4, 5, 1, 2000],\
          [-0.5603,-0.5600,-0.6201, -0.6198,3,0],\
          [-0.7807937278339523-1e-6, -0.7807937278339523+1e-6, -0.14686092684496543-1e-6, -0.14686092684496543+1e-6, 5, 0, 2000, 150]]          

colorFactor = 0

def divide_chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]

def F_threaded (x, sema, queue1, cf, ni, offset):
    # Section for filling data used in multithreading
    try:
        retval = array([growth(ci, cf, ni, offset) for ci in x])
        rp = pdumps (retval)
        if DEBUG:
            print ("BEFORE SENDING")
        queue1.put (rp)
        if DEBUG:
            print ("SENDING DONE")
    except BaseException as ki:
        queue1.close ()
        raise ki
    finally:
        sema.release ()
        

def F (x):
    # Callback for cplot
    global growthCounter
    global nrOfIterations
    global offset
    growthCounter = 0
    
    if N_THREADS == 1:
        # When non-threaded just fill the data.
        retval = array([growth(ci, colorFactor, nrOfIterations, offset) for ci in x])
        return retval
    else:
        try:
        
            from itertools import chain
        
            # When threaded then split up the work in several worker threads (processes)
            sema = Semaphore(MAXRUNNINGPROCESSES)
            divided = list(divide_chunks(x, CHUNKLENGTH))
            divLength = len(divided)
            processes = list()
            queues = list ()

            results2 = list ()
            for index in range(divLength):
                if DEBUG:
                    print ("Main    : create and start thread ", str(index))
                queue1 = Queue ()
                sema.acquire ()          
                x = Process(target=F_threaded, args= (divided[index], sema, queue1, colorFactor, nrOfIterations, offset))
                processes.append(x)
                queues.append (queue1)
                x.start()
                if DEBUG:
                    print ("Started")

            for index, process in enumerate(processes):
                if DEBUG:
                    print ("Main    : before joining process ", str(index))
                returnedData = queues [index].get()
                returnedObject = ploads (returnedData)
                results2.append (returnedObject)
                process.join()
                if DEBUG:
                    print ("Main    : process ", str(index), "done")

            retval = array(list(chain.from_iterable(results2)))
            if DEBUG:
                print ("Data returned")
            return retval
        except BaseException as be:
            print ("Worker process interrupted") # TODO Remove
            raise be
        

totalTotal = 0

def main ():
    global totalTotal
    global colorFactor
    global nrOfIterations
    global offset
    
    from matplotlib import pyplot as plt
    from cplot import plot as complex_plot
    from time import time
    
    for picNum in range(len(COORDS)):  # Change this loop for picking different pictures

        resetColorMap ()
        fig = plt.figure(figsize=(FIGSIZE,FIGSIZE),dpi=DPI) 
        t0 = time()

        nrOfIterations = ITERATIONS
        try:
            nrOfIterations = COORDS[picNum][6]
        except:
            pass
            
        offset = 0
        try:
            offset = COORDS[picNum][7]
        except:
            pass

        colorFactor = COORDS[picNum][5]
        complex_plot(F,(COORDS[picNum][0], COORDS[picNum][1], DIAGPOINTS),\
                       (COORDS[picNum][2], COORDS[picNum][3], DIAGPOINTS),\
                       linewidth=None,\
                       contours_abs=None, contours_arg=None,\
                       abs_scaling=COORDS[picNum][4],\
                       add_colorbars=False, add_axes_labels=False)
        t1 = time()
        total = t1-t0
        print ("Execution time (numeric generation) = " + str(round(total,2)))
        totalTotal += total
        
        newpath = r'pictures' 
        if not path.exists(newpath):
            makedirs(newpath)

        fig.savefig(f'pictures/mandelbrot_{DIAGPOINTS:04d}.{picNum:06d}.png', dpi=DPI) 
        t2 = time()                
        # NOTE: This seems to take a *lot* of memory in some cases. Optimization may be needed in picture generation. 
        total = t2-t1
        print ("Picture generated and saved. Time taken = " + str(round(total,2)))
 
        totalTotal += total
        plt.close ()
    print ("READY. Total execution time = " + str(round(totalTotal,2)))

if __name__ == '__main__':
    # This main section needed for running on Windows
    freeze_support()
    main ()

