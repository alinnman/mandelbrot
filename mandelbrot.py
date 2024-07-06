''' A simple program for drawing Mandelbrot fractals. For more information see README.md '''

try:
    from numpy      import array
    from os         import path, makedirs
    from mandeliter import growth
    import parameters as P

    # LAZY imports
    # from matplotlib import pyplot as plt
    # from picdata import COORDS
    # from time import time
    # from cplot import plot as complex_plot
    # NOTE: The cplot fork in my repositry https://github.com/alinnman/cplot2.git is recommended.
    # import itertools
    # from gc import collect
    # from multiprocessing import Process, Semaphore, Queue, freeze_support
    # from pickle import loads as ploads, dumps as pdumps
    # from importlib import util as importUtil
except BaseException as be:
    print ("Interrupted while loading packages")
    raise be

# COLOR_FACTOR = 0

def divide_chunks(l, n):
    ''' Split data into different chunks, to allow for paralell processing '''
    for i in range(0, len(l), n):
        yield l[i:i + n]

def F_threaded (x, sema, queue1, cf, ni, ofs, cs, pe, cl, dl, debug, cd, index):
    ''' Callback function '''
    # Section for filling data used in multithreading
    try:
        from pickle     import dumps as pdumps
        from mandeliter import growth
        retval = array([growth(ci, cf, ni, ofs, cs, pe, cl, dl, debug, cd, index) for ci in x])
        rp = pdumps (retval)
        del retval
        queue1.put (rp)
    except BaseException as ki:
        queue1.close ()
        raise ki
    finally:
        sema.release ()

def F (x):
    ''' Callback for cplot '''
    #global nrOfIterations
    #global offset

    if P.N_THREADS == 1:
        # When non-threaded just fill the data.
        retval = array([growth(ci, COLOR_FACTOR, nrOfIterations, offset, P.COLORSTEEPNESS,\
                               P.PARTIALESCAPECOUNT, P.CONVERGENCE_LIMIT, P.DIVERGENCE_LIMIT,\
                               P.DEBUG, P.COLORDAMPENING, 0) for ci in x])
        return retval
    else:
        try:
            from itertools       import chain
            from multiprocessing import Process, Semaphore, Queue
            from pickle          import loads as ploads
            from time            import time

            # When threaded then split up the work in several worker threads (processes)
            sema = Semaphore(P.N_THREADS)
            # Calculate reasonable chunk length
            chunk_length = int(max (len(x) / (P.N_THREADS*2), 50000))
            divided     = list(divide_chunks(x, chunk_length))
            div_length   = len(divided)
            processes   = list()
            queues      = list ()

            results2 = list ()
            for index in range(div_length):
                if P.DEBUG:
                    print ("Main    : create and start thread ", str(index))
                queue1 = Queue ()
                sema.acquire ()
                x = Process(target= F_threaded, \
                            args  = (divided[index], sema, queue1, COLOR_FACTOR, \
                                     nrOfIterations, offset, P.COLORSTEEPNESS,\
                                     P.PARTIALESCAPECOUNT,\
                                     P.CONVERGENCE_LIMIT, P.DIVERGENCE_LIMIT, P.DEBUG,\
                                     P.COLORDAMPENING, index))
                processes.append(x)
                queues.append (queue1)
                x.start()
                if P.DEBUG:
                    print ("Started")

            collection_start_time = time ()
            for index, process in enumerate(processes):
                if P.DEBUG:
                    print ("Main    : before joining process ", str(index))
                returned_data   = queues [index].get()
                returned_object = ploads (returned_data)
                del returned_data
                results2.append (returned_object)
                del returned_object
                process.join()
                if P.DEBUG:
                    print ("Main    : process ", str(index), "done")
            collection_end_time = time ()
            collection_time = collection_end_time - collection_start_time
            if P.DEBUG:
                print ("Collection time = " + str(round(collection_time,2)))

            retval = array(list(chain.from_iterable(results2)))
            del queues
            del processes
            del divided
            del results2
            if P.DEBUG:
                print ("Data returned")
            return retval
        except BaseException as bex:
            raise bex

TOTAL_TOTAL = 0

def main (args = None):
    ''' Main body of program. '''
    global TOTAL_TOTAL
    global COLOR_FACTOR
    global nrOfIterations
    global offset

    from matplotlib import pyplot as plt
    from cplot      import plot as complex_plot
    from time       import time
    from gc         import collect
    from sys        import argv
    from importlib  import util as importUtil
    from mandeliter import resetColorMap
    import picindices as PI

    if args is None:
        args = argv[1:]

    P.parseArguments (args)

    # Picture coordinates are imported dynamically
    spec = importUtil.spec_from_file_location("picdata", P.COORDFILE)
    picdata = importUtil.module_from_spec(spec)
    spec.loader.exec_module(picdata)

    newpath = r'pictures'
    if not path.exists(newpath):
        makedirs(newpath)

    nr_of_pics = len (picdata.COORDS)
    if P.SELECTOR == -1:
        selector = range (nr_of_pics)
    else:
        selector = range (P.SELECTOR, P.SELECTOR+1)
    for pic_num in selector:

        resetColorMap ()
        fig = plt.figure(figsize=(P.FIGSIZE,P.FIGSIZE),dpi=P.DPI)
        t0 = time()

        nrOfIterations = P.ITERATIONS
        try:
            nrOfIterations = picdata.COORDS[pic_num][PI.NROFITERATIONS]
            if nrOfIterations == -1:
                nrOfIterations = P.ITERATIONS
        except IndexError:
            pass

        offset = 0
        try:
            offset = picdata.COORDS[pic_num][PI.COLOR_OFFSET]
        except IndexError:
            pass

        COLOR_FACTOR = picdata.COORDS[pic_num][PI.COLOR_FACTOR]
        complex_plot(F,(picdata.COORDS[pic_num][PI.REAL_LEFT],\
                         picdata.COORDS[pic_num][PI.REAL_RIGHT], P.DIAGPOINTS),\
                       (picdata.COORDS[pic_num][PI.IMAG_LEFT],\
                         picdata.COORDS[pic_num][PI.IMAG_RIGHT], P.DIAGPOINTS),\
                       linewidth=None,\
                       contours_abs=None, contours_arg=None,\
                       abs_scaling=picdata.COORDS[pic_num][PI.ABS_SCALING],\
                       add_colorbars=False, add_axes_labels=False)
        t1 = time()
        total = t1-t0
        print ("\nExecution time (numeric generation) = " + str(round(total,2)))
        TOTAL_TOTAL += total

        if P.FILETYPE == "Screen":
            plt.show ()
        elif P.FILETYPE is not None:
            splitted_path = P.COORDFILE.split("/")
            used_name = splitted_path [len(splitted_path)-1]
            save_path =\
                  f'pictures/mandelbrot_{used_name}.{P.DIAGPOINTS:04d}.{pic_num:06d}.{P.FILETYPE}'
            fig.savefig(save_path, dpi=P.DPI)
            t2 = time()
            total = t2-t1
            print\
            ("Picture generated and saved to <"+save_path+">. Time taken = " + str(round(total,2)))
            TOTAL_TOTAL += total

        fig.clf ()
        plt.close ()
        collect ()

    print ("READY. Total execution time = " + str(round(TOTAL_TOTAL,2)))

if __name__ == '__main__':
    # This main section needed for running on Windows
    from multiprocessing import freeze_support
    freeze_support()
    main ()
