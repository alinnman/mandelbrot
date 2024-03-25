try:
    from numpy import ndarray, array, log, exp, frombuffer
    from os import environ, path, makedirs, _exit
    from pickle import loads as ploads, dumps as pdumps
    import parameters as P
    
    # LAZY imports
    # from matplotlib import pyplot as plt    
    # from picdata import COORDS
    # from time import time
    # from cplot import plot as complex_plot # NOTE: The cplot fork in my repositry https://github.com/alinnman/cplot2.git is recommended.     
    # import itertools
    # from gc import collect    
    # from multiprocessing import Process, Semaphore, Queue, freeze_support    
except BaseException as be: 
    print ("Interrupted while loading packages")
    raise be



if P.PARALELL:
    N_THREADS = P.MAXRUNNINGPROCESSES
    environ['OMP_NUM_THREADS'] = str(N_THREADS)
    environ['OPENBLAS_NUM_THREADS'] = str(N_THREADS)
    environ['MKL_NUM_THREADS'] = str(N_THREADS)
    environ['VECLIB_MAXIMUM_THREADS'] = str(N_THREADS)
    environ['NUMEXPR_NUM_THREADS'] = str(N_THREADS)
else:
    N_THREADS = 1

growthCounter = 0

def iter (x, c):
    return x*x + c

# The color map is used for caching color codes assigned
colorCodeMap = {}
def resetColorMap ():
    colorCodeMap = {}
    
def colorValue (counter, colorFactor, offset):
    # global P.COLORSTEEPNESS
    # global P.COLORDAMPENING
    counter = counter - offset
    if counter < 0.1:
        counter = 0.1
    return ((log(counter)**(P.COLORSTEEPNESS))/10)*1j*exp(-1j*counter*colorFactor)/P.COLORDAMPENING   

def colorCode (counter, useCache, colorFactor, offset):
    # global P.COLORSTEEPNESS
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
    # global P.DIVERGENCE_LIMIT
    # global P.CONVERGENCE_LIMIT

    for i in range (0,nrOfIterations):
        counter += 1
        newResult = iter (result, c)
        diffResult = newResult - result
        newAbsDiffResult = abs(diffResult)
        newAbsResult = abs(newResult)

        if (newAbsDiffResult < P.CONVERGENCE_LIMIT):
            # Convergence found
            reportGrowth ()
            if P.DEBUG:
                print("S", end='', flush=True)
            # Assign zero = convergence = Black color
            return 0
        elif newAbsResult > P.DIVERGENCE_LIMIT:
            # Divergence found. Find escape count and assign color.
            reportGrowth ()
            if P.DEBUG:
                print("E", end='', flush=True)
            if P.PARTIALESCAPECOUNT:
                ratio = (log(P.DIVERGENCE_LIMIT) - log(absResult)) / (log(newAbsResult) - log(absResult))
                return colorCode (counter + 0.5 + ratio, False, colorFactor, offset)
            else:
                return colorCode (counter, True, colorFactor, offset)
        result = newResult
        absDiffResult = newAbsDiffResult
        absResult = newAbsResult
    # Search exhausted. Assume looping.
    reportGrowth ()
    if P.DEBUG:
        print("!", end='', flush=True)
    return 0

colorFactor = 0

def divide_chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]

def F_threaded (x, sema, queue1, cf, ni, offset):
    # Section for filling data used in multithreading
    try:
        retval = array([growth(ci, cf, ni, offset) for ci in x])
        rp = pdumps (retval)
        del retval
        if P.DEBUG:
            print ("BEFORE SENDING")
        queue1.put (rp)
        if P.DEBUG:
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
            from multiprocessing import Process, Semaphore, Queue
        
            # When threaded then split up the work in several worker threads (processes)
            sema = Semaphore(N_THREADS)
            divided = list(divide_chunks(x, P.CHUNKLENGTH))
            divLength = len(divided)
            processes = list()
            queues = list ()

            results2 = list ()
            for index in range(divLength):
                if P.DEBUG:
                    print ("Main    : create and start thread ", str(index))
                queue1 = Queue ()
                sema.acquire ()          
                x = Process(target=F_threaded, args= (divided[index], sema, queue1, colorFactor, nrOfIterations, offset))
                processes.append(x)
                queues.append (queue1)
                x.start()
                if P.DEBUG:
                    print ("Started")

            for index, process in enumerate(processes):
                if P.DEBUG:
                    print ("Main    : before joining process ", str(index))
                returnedData = queues [index].get()
                returnedObject = ploads (returnedData)
                del returnedData
                results2.append (returnedObject)
                del returnedObject
                process.join()
                if P.DEBUG:
                    print ("Main    : process ", str(index), "done")

            retval = array(list(chain.from_iterable(results2)))
            del results2
            if P.DEBUG:
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
    from gc import collect
    from picdata import COORDS

    for picNum in range(len(COORDS)):  # Change this loop for picking different pictures

        resetColorMap ()
        fig = plt.figure(figsize=(P.FIGSIZE,P.FIGSIZE),dpi=P.DPI)
        t0 = time()

        nrOfIterations = P.ITERATIONS
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
        complex_plot(F,(COORDS[picNum][0], COORDS[picNum][1], P.DIAGPOINTS),\
                       (COORDS[picNum][2], COORDS[picNum][3], P.DIAGPOINTS),\
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

        fig.savefig(f'pictures/mandelbrot_{P.DIAGPOINTS:04d}.{picNum:06d}.png', dpi=P.DPI) 
        t2 = time()
        # NOTE: This seems to take a *lot* of memory in some cases. Optimization may be needed in picture generation. 
        total = t2-t1
        print ("Picture generated and saved. Time taken = " + str(round(total,2)))

        totalTotal += total
        fig.clf ()
        plt.close ()
        collect ()

    print ("READY. Total execution time = " + str(round(totalTotal,2)))

if __name__ == '__main__':
    # This main section needed for running on Windows
    from multiprocessing import freeze_support
    freeze_support()
    main ()

