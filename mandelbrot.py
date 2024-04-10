try:
    from numpy import array
    from os import environ, path, makedirs
    import parameters as P
    from mandeliter import growth

    # LAZY imports
    # from matplotlib import pyplot as plt
    # from picdata import COORDS
    # from time import time
    # from cplot import plot as complex_plot # NOTE: The cplot fork in my repositry https://github.com/alinnman/cplot2.git is recommended.     
    # import itertools
    # from gc import collect
    # from multiprocessing import Process, Semaphore, Queue, freeze_support
    # from pickle import loads as ploads, dumps as pdumps
    # from importlib import util as importUtil
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

colorFactor = 0

def divide_chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]

def F_threaded (x, sema, queue1, cf, ni, offset, cs, pe, cl, dl, debug, cd):
    # Section for filling data used in multithreading
    try:
        from pickle import dumps as pdumps
        from mandeliter import growth
        retval = array([growth(ci, cf, ni, offset, cs, pe, cl, dl, debug, cd) for ci in x])
        rp = pdumps (retval)
        del retval
        queue1.put (rp)
    except BaseException as ki:
        queue1.close ()
        raise ki
    finally:
        sema.release ()


def F (x):
    # Callback for cplot
    global nrOfIterations
    global offset

    if N_THREADS == 1:
        # When non-threaded just fill the data.
        retval = array([growth(ci, colorFactor, nrOfIterations, offset, P.COLORSTEEPNESS,\
                               P.PARTIALESCAPECOUNT, P.CONVERGENCE_LIMIT, P.DIVERGENCE_LIMIT,\
                               P.DEBUG, P.COLORDAMPENING) for ci in x])
        return retval
    else:
        try:
            from itertools import chain
            from multiprocessing import Process, Semaphore, Queue
            from pickle import loads as ploads

            # When threaded then split up the work in several worker threads (processes)
            sema = Semaphore(N_THREADS)
            # Calculate reasonable chunk length
            chunkLength = int(max (len(x) / 8, 50000))
            divided = list(divide_chunks(x, chunkLength))
            divLength = len(divided)
            processes = list()
            queues = list ()

            results2 = list ()
            for index in range(divLength):
                if P.DEBUG:
                    print ("Main    : create and start thread ", str(index))
                queue1 = Queue ()
                sema.acquire ()
                x = Process(target=F_threaded, \
                            args= (divided[index], sema, queue1, colorFactor, \
                                   nrOfIterations, offset, P.COLORSTEEPNESS, P.PARTIALESCAPECOUNT,\
                                   P.CONVERGENCE_LIMIT, P.DIVERGENCE_LIMIT, P.DEBUG, P.COLORDAMPENING))
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
            del queues
            del processes
            del divided
            del results2
            if P.DEBUG:
                print ("Data returned")
            return retval
        except BaseException as be:
            raise be

totalTotal = 0

def main (args = None):
    global totalTotal
    global colorFactor
    global nrOfIterations
    global offset

    from matplotlib import pyplot as plt
    from cplot import plot as complex_plot
    from time import time
    from gc import collect
    from sys import argv
    from importlib import util as importUtil
    import picindices as PI
    from mandeliter import resetColorMap
    
    if args == None:
        args = argv[1:]
   
    P.parseArguments (args)
    
    # Picture coordinates are imported dynamically 
    spec = importUtil.spec_from_file_location("picdata", P.COORDFILE)
    picdata = importUtil.module_from_spec(spec)
    spec.loader.exec_module(picdata)

    newpath = r'pictures'
    if not path.exists(newpath):
        makedirs(newpath)

    nrOfPics = len (picdata.COORDS)
    if P.SELECTOR == -1:
        selector = range (nrOfPics)
    else:
        selector = range (P.SELECTOR, P.SELECTOR+1)
    for picNum in selector:   

        resetColorMap ()
        fig = plt.figure(figsize=(P.FIGSIZE,P.FIGSIZE),dpi=P.DPI)
        t0 = time()

        nrOfIterations = P.ITERATIONS
        try:
            nrOfIterations = picdata.COORDS[picNum][PI.NROFITERATIONS]
            if nrOfIterations == -1:
                nrOfIterations = P.ITERATIONS
        except:
            pass

        offset = 0
        try:
            offset = picdata.COORDS[picNum][PI.COLOR_OFFSET]
        except:
            pass

        colorFactor = picdata.COORDS[picNum][PI.COLOR_FACTOR]
        complex_plot(F,(picdata.COORDS[picNum][PI.REAL_LEFT], picdata.COORDS[picNum][PI.REAL_RIGHT], P.DIAGPOINTS),\
                       (picdata.COORDS[picNum][PI.IMAG_LEFT], picdata.COORDS[picNum][PI.IMAG_RIGHT], P.DIAGPOINTS),\
                       linewidth=None,\
                       contours_abs=None, contours_arg=None,\
                       abs_scaling=picdata.COORDS[picNum][PI.ABS_SCALING],\
                       add_colorbars=False, add_axes_labels=False)
        t1 = time()
        total = t1-t0
        print ("Execution time (numeric generation) = " + str(round(total,2)))
        totalTotal += total

        splittedPath = P.COORDFILE.split("/")
        usedName = splittedPath [len(splittedPath)-1]
        
        #from PIL import Image
        #import numpy as np
        #import matplotlib.pyplot as plt

        #data = np.random.random((100, 100))
        #cm = plt.get_cmap('viridis')
        #img = Image.fromarray((cm(data)[:, :, :3] * 255).astype(np.uint8))
        #img.save('image.png')        
        
        savePath = f'pictures/mandelbrot_{usedName}.{P.DIAGPOINTS:04d}.{picNum:06d}.tif'
        fig.savefig(savePath, dpi=P.DPI) 
        t2 = time()
        total = t2-t1
        print ("Picture generated and saved to <"+savePath+">. Time taken = " + str(round(total,2)))

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

