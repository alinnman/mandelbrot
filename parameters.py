import argparse
from multiprocessing import cpu_count

# Picture rendering
DPI=300
DIAGPOINTS=100
FIGSIZE=20

# Debug
DEBUG=False

# Function evaluation and iteration
ITERATIONS=1000
DIVERGENCE_LIMIT = 2
CONVERGENCE_LIMIT = 1e-6

# Process execution
PARALELL = True
CHUNKLENGTH = 50000
MAXRUNNINGPROCESSES = max(1, cpu_count()-4) 

# Detailed color rendering
PARTIALESCAPECOUNT = True
## Experimental parameters which may need to be adjusted for deep zooms with small gradients
COLORSTEEPNESS = 3
COLORDAMPENING = 1

# Picture selection
COORDFILE = "picdata/picdata.py"
SELECTOR = -1

def parseArguments (args): 
    global DPI, DIAGPOINTS, ITERATIONS, CHUNKLENGTH, MAXRUNNINGPROCESSES, COORDFILE, COLORSTEEPNESS, SELECTOR
    
    parser = argparse.ArgumentParser(prog = "mandelbrot", description='Mandelbrot plotter',\
                                     epilog='This is a simple demo of plotting the Mandelbrot fractal')

    parser.add_argument("-dpi", "--dots_per_inch_resolution",\
    help="Resolution of output file (in DPI). Default="+str(DPI), \
                        action="store", default=int(DPI))
    parser.add_argument("-dp", "--diagram_points",\
    help="Sample width of diagram. Default="+str(DIAGPOINTS), \
                        action="store", default=int(DIAGPOINTS))
    parser.add_argument("-it", "--iterations",\
    help="Max nr of iterations. Default="+str(ITERATIONS), \
                        action="store", default=int(ITERATIONS))     
    parser.add_argument("-cl", "--chunk_length",\
    help="Number of pixels handled by each thread instance. Default="+str(CHUNKLENGTH), \
                        action="store", default=int(CHUNKLENGTH))    
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
                                      
    argsParsed = parser.parse_args(args)
    
    va = vars(argsParsed)

    DPI                 = int (va ['dots_per_inch_resolution' ])
    DIAGPOINTS          = int (va ['diagram_points'           ])
    ITERATIONS          = int (va ['iterations'               ])
    CHUNKLENGTH         = int (va ['chunk_length'             ]) 
    MAXRUNNINGPROCESSES = int (va ['max_running_processes'    ])     
    COORDFILE           =      va ['coordinate_file'           ]
    COLORSTEEPNESS      = int (va ['color_steepness'          ])
    SELECTOR            = int (va ['picture_selector'         ])
    
    
    
