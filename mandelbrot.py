from matplotlib import pyplot as plt
from numpy import ndarray, array, log, exp, frombuffer
from os import environ
from time import time
from cplot import plot as complex_plot
from multiprocessing import Process, Semaphore, Queue, freeze_support
import itertools
from pickle import loads as ploads, dumps as pdumps

DPI = 400
#POWER = 2
DIAGPOINTS =2000
FIGSIZE=20
ITERATIONS=10000
DEBUG=False

PARALELL = True
CHUNKLENGTH = 100000
#CHUNKLENGTH = 500000
MAXRUNNINGPROCESSES = 4

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
    result = x*x + c
    return result

colorCodeMap = {}
def resetColorMap ():
    colorCodeMap = {}

def colorCode (counter):
    global colorFactor
    retVal = 0
    try:
        retVal = colorCodeMap [counter]
        return retVal
    except:
        retVal = (log(counter)**3/10)*1j*exp(-1j*counter*colorFactor)
        colorCodeMap [counter] = retVal
        return retVal

def reportGrowth ():
    global growthCounter
    growthCounter += 1
    if growthCounter % 10000 == 0:
        print(".", end='', flush=True)

def growth (c):
    counter, result = 0, 0

    for i in range (0,ITERATIONS):
        counter += 1
        newResult = iter (result, c)
        diffResult = newResult - result
        absDiffResult = abs(diffResult)

        if absDiffResult < 1e-6:
            reportGrowth ()
            if DEBUG:
                print("S", end='', flush=True)
            return 0
        elif absDiffResult > 1e3:
            reportGrowth ()
            cc = colorCode (counter)
            if DEBUG:
                print("E", end='', flush=True)            
            return colorCode (counter)
        result = newResult
    reportGrowth ()
    if DEBUG:
        print("!", end='', flush=True)
    return 0


COORDS = [[-2.2, 0.8,-1.3, 1.3, 2, 0],\
          [-0.4, 0.2, 0.5, 1.2, 2, 0],\
          [-0.2, -0.1, 1, 1.1, 2, 0],\
          [-0.184, -0.16, 1.06, 1.08, 2, 0],\
          [-0.176, -0.1725, 1.07, 1.073, 2, 0],\
          [-0.5625, -0.5476, -0.6300, -0.6165, 2.5, 0],\
          [-0.74453892-1e-4,-0.74453892+1e-4,0.12172418-1e-4,0.12172418+1e-4, 5, 1],\
          [-0.5603,-0.5600,-0.6201, -0.6198,3,0],\
          [-0.56014,-0.56006,-0.61993, -0.61987,4,0],\
          [-0.5600886, -0.5600883, -0.61988035, -0.6198800, 5,0]]
          
colorFactor = 0

def divide_chunks(l, n): 
    for i in range(0, len(l), n):  
        yield l[i:i + n] 

def F_simple (x, sema, queue1):
    try:
        retval = array([growth(ci) for ci in x])
        rp = pdumps (retval)
        if DEBUG:
            print ("BEFORE SENDING")
        queue1.put (rp)
        if DEBUG:
            print ("SENDING DONE")

    finally:
        sema.release ()

def F (x):
    global growthCounter
    growthCounter = 0
    if N_THREADS == 1:
        retval = array([growth(ci) for ci in x])
        return retval   
    else:
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
            x = Process(target=F_simple, args= (divided[index], sema, queue1))
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
            
        retval22 = array(list(itertools.chain.from_iterable(results2)))
        if DEBUG:
            print ("Data returned")
 
        return retval22
        

totalTotal = 0

def main ():
    global totalTotal
    for picNum in ([9]):

        resetColorMap ()
        fig = plt.figure(figsize=(FIGSIZE,FIGSIZE),dpi=DPI) 
        t0 = time()

        colorFactor = COORDS[picNum][5]
        complex_plot(F,(COORDS[picNum][0], COORDS[picNum][1], DIAGPOINTS),\
                       (COORDS[picNum][2], COORDS[picNum][3], DIAGPOINTS),\
                       linewidth=None,\
                       contours_abs=None, contours_arg=None,\
                       abs_scaling=COORDS[picNum][4],\
                       add_colorbars=False, add_axes_labels=False)
        t1 = time()
        total = t1-t0
        print ("Execution time = " + str(total))
        totalTotal += total

        fig.savefig(f'mandelbrot_{DIAGPOINTS:04d}.{picNum:06d}.png', dpi=DPI)
        print ("Picture saved")
        plt.close ()
    print ("READY. Total execution time = " + str(totalTotal))

if __name__ == '__main__':
    freeze_support()
    main ()

