You must start by cloning my repository cplot2. It is a fork of the official PyPi cplot library. 

    git clone https://github.com/alinnman/cplot2.git
    pip uninstall cplot # If you already had cplot installed
    cd <directory of the clone you just made>
    pip install . 

Then just clone or fork this repository and run the main Python file (mandelbrot.py). 

    git clone https://github.com/alinnman/mandelbrot.git
	pip install -r requirements.txt

The program uses a Cython module for computation speed. 
See attached file build.sh which builds the C-code and executable for a Linux environment. 

Parameters are shown using help switch

    python mandelbrot.py -h

For examples see the <a href="README.md">README file</a>


