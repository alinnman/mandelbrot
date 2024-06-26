# Requirements

* Windows 10/11 or Linux. 
* Installation of C compiler
* Python 3 environment
* Git for cloning or forking the code

# Build and run

You must start by cloning <a href="https://github.com/alinnman/cplot2">my repository cplot2</a>. It is a fork of <a href="https://github.com/nschloe/cplot.git">the official PyPi cplot library</a>. 

    git clone https://github.com/alinnman/cplot2.git
    pip uninstall cplot # If you already had cplot installed
    cd <directory of the clone you just made>
    pip install . 

Then just clone or fork <a href="https://github.com/alinnman/mandelbrot.git">this repository</a> to a suitable location. Install dependent libraries. 

    git clone https://github.com/alinnman/mandelbrot.git
	pip install -r requirements.txt

The program uses a Cython module for computation speed. 
Execute one of the attached scripts <a href="build.sh">``build.sh``</a> (Linux) or <a href="build.cmd">``build.cmd``</a> (Windows) which builds the C-code and executable. 

Now you can run the program. Specifying no arguments will just generate a test suite. All generated images will be written to the ``pictures`` subdirectory. 

    python mandelbrot.py
	
You can also try running the tests

    pytest

Parameters are shown using help switch

    python mandelbrot.py -h

For examples see the <a href="README.md">README file</a>

# Tips on environment (Python and C)

I have used <a href="https://www.anaconda.com/download/">Anaconda</a> as <b>Python</b> environment, both on Windows and Linux. 
On Windows I have installed Visual Studio wich complete C compiler support. On Linux I use the standard C compiler supplied with the Ubuntu distribution. 
