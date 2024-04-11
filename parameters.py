import argparse
from multiprocessing import cpu_count
from os import environ

# Picture rendering
DPI=300
DIAGPOINTS=1000
FIGSIZE=20
FILETYPE="PNG"

# Debug
DEBUG=False

# Function evaluation and iteration
ITERATIONS=1000
DIVERGENCE_LIMIT = 2
CONVERGENCE_LIMIT = 1e-6

# Process execution
#PARALELL = True
#CHUNKLENGTH = 50000
MAXRUNNINGPROCESSES = max(1, cpu_count()-4) 

# Detailed color rendering
PARTIALESCAPECOUNT = True
## Experimental parameters which may need to be adjusted for deep zooms with small gradients
COLORSTEEPNESS = 3
COLORDAMPENING = 1

# Picture selection
COORDFILE = "picdata/picdata.py"
SELECTOR = -1

N_THREADS = -1

def parseArguments (args): 
    global DPI, DIAGPOINTS, ITERATIONS, CHUNKLENGTH, MAXRUNNINGPROCESSES, \
           COORDFILE, COLORSTEEPNESS, SELECTOR, PARTIALESCAPECOUNT, FILETYPE, N_THREADS, DEBUG
    
    parser = argparse.ArgumentParser(prog = "mandelbrot", description='Mandelbrot plotter',\
                                     epilog='This is a simple demo of plotting the Mandelbrot fractal')

    parser.add_argument("-dpi", "--dots_per_inch_resolution",\
    help="Resolution of output file (in DPI). Default="+str(DPI), \
                        action="store", default=int(DPI))
    parser.add_argument("-dp", "--diagram_points",\
    help="Sample width of diagram. Default="+str(DIAGPOINTS), \
                        action="store", default=int(DIAGPOINTS))
    parser.add_argument("-ft", "--file_type",\
    help="File type of generated picture (TIF, PNG, JPG, SVG, Screen, None). Default="+str(FILETYPE), \
                        action="store", default=FILETYPE)                        
    parser.add_argument("-it", "--iterations",\
    help="Max nr of iterations. Default="+str(ITERATIONS), \
                        action="store", default=int(ITERATIONS))     
    '''
    parser.add_argument("-cl", "--chunk_length",\
    help="Number of pixels handled by each thread instance. Default="+str(CHUNKLENGTH), \
                        action="store", default=int(CHUNKLENGTH))    
    '''
    parser.add_argument("-mp", "--max_running_processes",\
    help="Maximum number of concurrent processes. Default="+str(MAXRUNNINGPROCESSES), \
                        action="store", default=int(MAXRUNNINGPROCESSES))                 
    parser.add_argument("-cd", "--coordinate_file",\
    help="File with used coordinates for pictures. Default="+COORDFILE, \
                        action="store", default=COORDFILE)     
    parser.add_argument("-cs", "--color_steepness",\
    help="Steepness in colors (contrast). Default="+str(COLORSTEEPNESS), \
                        action="store", default=COLORSTEEPNESS)      
    parser.add_argument("-sel", "--picture_selector",\
    help="Selection of a single image in a picture set. Default="+str(SELECTOR)+" (select all pictures)", \
                        action="store", default=SELECTOR)   
    parser.add_argument("-pe", "--partial_escape_count",\
    help="Use partial escape count. Will produce prettier images but costs some CPU time. Default = "+str(PARTIALESCAPECOUNT), \
                        action="store", default=PARTIALESCAPECOUNT)   

    parser.add_argument("-d","--debug", \
                       help="Show debug info. Default = Not Set", \
                       action="store_const", const="True")                         
                                      
    argsParsed = parser.parse_args(args)
    
    va = vars(argsParsed)

    DPI                 = int       (va ['dots_per_inch_resolution'])
    DIAGPOINTS          = int       (va ['diagram_points'          ])
    ITERATIONS          = int       (va ['iterations'              ])
    #CHUNKLENGTH         = int       (va ['chunk_length'            ]) 
    MAXRUNNINGPROCESSES = int       (va ['max_running_processes'   ])     
    COORDFILE           =            va ['coordinate_file'         ]
    COLORSTEEPNESS      = int       (va ['color_steepness'         ])
    SELECTOR            = int       (va ['picture_selector'        ])
    PARTIALESCAPECOUNT  = bool      (va ['partial_escape_count'    ] != str(False))
    FILETYPE            =            va ['file_type'               ]
    if FILETYPE.upper() == "SCREEN":
        FILETYPE = "Screen"
    elif FILETYPE.upper() == "NONE":
        FILETYPE = None 
    DEBUG               =           (va ['debug'                   ]) == str(True) 
        
    if MAXRUNNINGPROCESSES > 1:
        N_THREADS = MAXRUNNINGPROCESSES
        environ['OMP_NUM_THREADS'] = str(N_THREADS)
        environ['OPENBLAS_NUM_THREADS'] = str(N_THREADS)
        environ['MKL_NUM_THREADS'] = str(N_THREADS)
        environ['VECLIB_MAXIMUM_THREADS'] = str(N_THREADS)
        environ['NUMEXPR_NUM_THREADS'] = str(N_THREADS)
    else:
        N_THREADS = 1
        
        
        
    


    
    
    
